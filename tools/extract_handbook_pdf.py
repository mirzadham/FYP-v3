"""
PDF Handbook Extraction Script for Academic Advisor.

This script extracts course information from faculty handbook PDFs using LLM-based
extraction. It handles varying PDF formats by using GPT to intelligently parse
course data into a unified schema.

Usage:
    cd AcademicAdvisor-Chatbot-V3
    python tools/extract_handbook_pdf.py --pdf data/handbook/pdf/fpertanian.pdf

Requirements:
    - OPENAI_API_KEY environment variable set
    - pymupdf, openai packages installed
"""

import os
import re
import json
import pickle
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
import pymupdf  # PyMuPDF

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PDF_DIR = PROJECT_ROOT / "data" / "handbook" / "pdf"
JSON_DIR = PROJECT_ROOT / "data" / "handbook" / "json"
EMBEDDINGS_DIR = PROJECT_ROOT / "data" / "handbook" / "embeddings"

# Ensure output directories exist
JSON_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

# Course code pattern - matches codes like AGR1001, CCS3002, PRT2001, etc.
COURSE_CODE_PATTERN = re.compile(r'\b([A-Z]{2,4}\d{3,4})\b')


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from a PDF file using PyMuPDF."""
    print(f"📄 Extracting text from: {pdf_path}")
    
    doc = pymupdf.open(pdf_path)
    page_count = doc.page_count
    text = ""
    
    for page_num in range(page_count):
        page = doc.load_page(page_num)
        text += f"\n--- Page {page_num + 1} ---\n"
        text += page.get_text()
    
    doc.close()
    print(f"   Extracted {len(text):,} characters from {page_count} pages")
    return text


def chunk_by_course_code(text: str) -> List[Dict[str, str]]:
    """Split text into chunks, each containing one course's information.
    
    Only matches course codes at the START of a line to avoid picking up
    prerequisite course codes mentioned in the middle of text.
    """
    print("🔍 Detecting course codes and chunking text...")
    
    # Pattern to match course codes at the START of a line only
    # This prevents matching prerequisite codes like "Prasyarat : ENG3001"
    line_start_pattern = re.compile(r'^([A-Z]{2,4}\d{3,4})\s', re.MULTILINE)
    
    # Find all course code positions (only at line starts)
    matches = list(line_start_pattern.finditer(text))
    
    if not matches:
        print("   ⚠️ No course codes found!")
        return []
    
    # Deduplicate consecutive matches for the same course code
    # (in case same code appears multiple times at line starts)
    unique_matches = []
    seen_positions = set()
    for match in matches:
        code = match.group(1)
        # Check if this is a new course block (not just a reference)
        # by looking at some context after the code
        pos = match.start()
        if pos not in seen_positions:
            unique_matches.append(match)
            seen_positions.add(pos)
    
    # Create chunks between consecutive course codes
    chunks = []
    for i, match in enumerate(unique_matches):
        start = match.start()
        # End at the next course code or end of text
        end = unique_matches[i + 1].start() if i + 1 < len(unique_matches) else len(text)
        
        chunk_text = text[start:end].strip()
        course_code = match.group(1)
        
        # Skip very short chunks (likely false positives or page headers)
        # Also skip if the chunk doesn't contain typical course info patterns
        if len(chunk_text) > 100:
            # Additional validation: check if chunk looks like a course definition
            # (should have credit hours pattern or "Prasyarat"/"Prerequisite")
            has_credits = bool(re.search(r'\d\s*\(\s*\d\+\d\s*\)', chunk_text))
            has_prereq = 'prasyarat' in chunk_text.lower() or 'prerequisite' in chunk_text.lower()
            has_description = len(chunk_text) > 200  # Course descriptions are usually longer
            
            if has_credits or has_prereq or has_description:
                chunks.append({
                    "course_code": course_code,
                    "raw_text": chunk_text
                })
    
    print(f"   Found {len(chunks)} potential course chunks")
    return chunks


def extract_faculty_name(pdf_path: str) -> str:
    """Extract faculty name from PDF filename."""
    filename = Path(pdf_path).stem
    # Convert filename to readable faculty name
    name_mapping = {
        "fpertanian": "Fakulti Pertanian",
        "fsktm": "Fakulti Sains Komputer dan Teknologi Maklumat",
        "fkejuruteraan": "Fakulti Kejuruteraan",
        "fsains": "Fakulti Sains",
        "fperubatan": "Fakulti Perubatan dan Sains Kesihatan",
        "fveterinar": "Fakulti Perubatan Veterinar",
        "fbmk": "Fakulti Bahasa Moden dan Komunikasi",
        "spe": "Sekolah Perniagaan dan Ekonomi",
        "f_pengajian_pendidikan": "Fakulti Pengajian Pendidikan",
        "Fakulti_Perhutanan_dan_Alam_Sekitar": "Fakulti Perhutanan dan Alam Sekitar",
        "Fakulti_Sains_Pertanian_dan_Perhutanan": "Fakulti Sains Pertanian dan Perhutanan",
        "FAKULTI SAINS DAN TEKNOLOGI MAKANAN": "Fakulti Sains dan Teknologi Makanan",
        "FAKULTI EKOLOGI MANUSIA": "Fakulti Ekologi Manusia",
        "Fakulti_Rekabentuk_dan_Senibina": "Fakulti Rekabentuk dan Senibina",
        "Fakulti_Bioteknologi_dan_Sains_Biomolekul": "Fakulti Bioteknologi dan Sains Biomolekul",
    }
    return name_mapping.get(filename.lower(), filename.replace("_", " ").title())


def extract_course_info(client: OpenAI, chunk: Dict[str, str], faculty_name: str) -> Optional[Dict]:
    """Use LLM to extract structured course information from a text chunk."""
    
    prompt = f"""You are extracting course information from a Malaysian university handbook.
Extract the following fields from this text. Return ONLY valid JSON, no markdown.

If a field is not found, use null. For prerequisites, return an empty array [] if none.

Schema:
{{
  "course_code": "string",
  "course_name_malay": "string or null",
  "course_name_english": "string or null", 
  "credits": "string (e.g., '3(3+0)' or '3 credits')",
  "prerequisites": ["list of course codes"],
  "description_malay": "string or null",
  "description_english": "string or null",
  "department": "string or null"
}}

Text to extract from:
---
{chunk['raw_text'][:2000]}
---

Return ONLY the JSON object, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean up response if it has markdown code blocks
        if result_text.startswith("```"):
            result_text = re.sub(r'^```json?\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)
        
        course_data = json.loads(result_text)
        course_data["faculty"] = faculty_name
        course_data["source_chunk"] = chunk["raw_text"][:500]  # Keep first 500 chars for reference
        
        return course_data
        
    except json.JSONDecodeError as e:
        print(f"   ⚠️ JSON parse error for {chunk['course_code']}: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Error extracting {chunk['course_code']}: {e}")
        return None


def generate_embedding(client: OpenAI, course: Dict) -> List[float]:
    """Generate embedding for a course's searchable content."""
    
    # Create rich searchable text
    searchable_text = f"""
Course: {course.get('course_code', '')} - {course.get('course_name_english', '')}
Malay Name: {course.get('course_name_malay', '')}
Faculty: {course.get('faculty', '')}
Department: {course.get('department', '')}
Credits: {course.get('credits', '')}
Prerequisites: {', '.join(course.get('prerequisites', [])) or 'None'}

Description (English): {course.get('description_english', '')}
Description (Malay): {course.get('description_malay', '')}
""".strip()
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=searchable_text
    )
    
    return response.data[0].embedding


def save_results(courses: List[Dict], embeddings: Dict, pdf_path: str):
    """Save extracted courses to JSON and embeddings to pickle."""
    
    base_name = Path(pdf_path).stem
    
    # Save JSON
    json_path = JSON_DIR / f"{base_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(courses)} courses to: {json_path}")
    
    # Save embeddings
    embeddings_path = EMBEDDINGS_DIR / f"{base_name}_embeddings.pkl"
    with open(embeddings_path, "wb") as f:
        pickle.dump(embeddings, f)
    print(f"💾 Saved embeddings to: {embeddings_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract course info from faculty handbook PDFs")
    parser.add_argument("--pdf", required=True, help="Path to the PDF file")
    parser.add_argument("--skip-embeddings", action="store_true", help="Skip embedding generation")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   PDF Handbook Extraction Pipeline")
    print("=" * 60)
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Step 1: Extract text from PDF
    raw_text = extract_text_from_pdf(args.pdf)
    
    # Step 2: Chunk by course code
    chunks = chunk_by_course_code(raw_text)
    
    if not chunks:
        print("❌ No courses found in PDF!")
        return
    
    # Step 3: Extract course info using LLM
    faculty_name = extract_faculty_name(args.pdf)
    print(f"\n🎓 Faculty: {faculty_name}")
    print(f"🔄 Extracting course information using LLM...")
    
    courses = []
    for i, chunk in enumerate(chunks):
        print(f"   [{i+1}/{len(chunks)}] Processing {chunk['course_code']}...", end=" ")
        course_data = extract_course_info(client, chunk, faculty_name)
        
        if course_data:
            courses.append(course_data)
            name = course_data.get('course_name_english') or course_data.get('course_name_malay') or 'Unknown'
            print(f"✅ {name[:40]}")
        else:
            print("⏭️ Skipped")
    
    print(f"\n✅ Successfully extracted {len(courses)} courses")
    
    # Step 4: Generate embeddings
    embeddings = {}
    if not args.skip_embeddings:
        print(f"\n🔄 Generating embeddings...")
        for i, course in enumerate(courses):
            code = course.get('course_code', f'unknown_{i}')
            print(f"   [{i+1}/{len(courses)}] Embedding {code}...", end=" ")
            try:
                embedding = generate_embedding(client, course)
                embeddings[code] = {
                    "course": course,
                    "embedding": embedding
                }
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
    
    # Step 5: Save results
    print()
    save_results(courses, embeddings, args.pdf)
    
    print("\n" + "=" * 60)
    print(f"   ✅ Pipeline Complete!")
    print(f"   Courses extracted: {len(courses)}")
    print(f"   Embeddings generated: {len(embeddings)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

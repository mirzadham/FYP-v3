"""
Improved Academic Rules PDF Extraction Script.

Key Improvements:
1. Semantic Chunking: Splits text by 'Rule', 'Part', or 'Schedule' boundaries instead of pages.
2. Noise Removal: Filters out headers, footers, and page numbers.
3. Context Preservation: Ensures multi-page rules are kept as single text blocks.
"""

import re
import json
import pickle
import argparse
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
import pymupdf  # PyMuPDF

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PDF_PATH = PROJECT_ROOT / "data" / "handbook" / "academic_rules" / "academic_rules.pdf"
JSON_OUTPUT_PATH = PROJECT_ROOT / "data" / "handbook" / "json" / "rules.json"
EMBEDDINGS_OUTPUT_PATH = PROJECT_ROOT / "data" / "handbook" / "embeddings" / "rules_embeddings.pkl"


def clean_page_text(text: str) -> str:
    """
    Cleans headers, footers, and page numbers from raw PDF text.
    Adjust these patterns based on the specific document layout.
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        content = line.strip()
        # Skip empty lines
        if not content:
            continue
        # Skip Page numbers (e.g., "43", "Page 2")
        if re.match(r'^Page \d+$', content) or re.match(r'^\d+$', content):
            continue
        # Skip Document Titles often repeated in headers
        if "UNIVERSITI PUTRA MALAYSIA" in content:
            continue
        if "(ACADEMIC MATTERS FOR UNDERGRADUATES)" in content:
            continue
            
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines)


def extract_text_semantically(pdf_path: Path) -> List[str]:
    """
    Extracts text and splits it into semantic chunks (Rules, Parts, Schedules).
    Returns a list of strings, where each string is a complete Rule or Schedule.
    """
    print(f"📄 Extracting and parsing structure from: {pdf_path}")
    
    doc = pymupdf.open(pdf_path)
    full_text = ""
    
    # 1. Aggregate all text first (removing page breaks which disrupt flow)
    for page in doc:
        full_text += clean_page_text(page.get_text()) + "\n"
    
    doc.close()

    # 2. Define Regex Patterns for Document Structure
    # Matches "PART A", "PART B"
    part_pattern = re.compile(r'\n(PART [A-Z].*?)(?=\n)', re.IGNORECASE)
    
    # Matches "1. Short Title", "3. Registration" (Number + Dot + Space + Title)
    # We look for a number at the start of a line
    rule_pattern = re.compile(r'\n(\d+\.\s+[A-Z][a-zA-Z\s\(\)\-\,]+)(?=\n)', re.MULTILINE)
    
    # Matches "First Schedule", "Second Schedule"
    schedule_pattern = re.compile(r'\n((?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth)\s+Schedule.*?)(?=\n)', re.IGNORECASE)

    # 3. Intelligent Splitting
    # We will build a list of (index, type, title) markers to slice the text
    markers = []
    
    for match in part_pattern.finditer(full_text):
        markers.append((match.start(), "PART", match.group(1).strip()))
        
    for match in rule_pattern.finditer(full_text):
        markers.append((match.start(), "RULE", match.group(1).strip()))
        
    for match in schedule_pattern.finditer(full_text):
        markers.append((match.start(), "SCHEDULE", match.group(1).strip()))

    # Sort markers by position
    markers.sort(key=lambda x: x[0])
    
    chunks = []
    
    # If no markers found, return full text (fallback)
    if not markers:
        print("   ⚠️ No structural markers found. Returning raw chunks.")
        return [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]

    # Slice text based on markers
    for i in range(len(markers)):
        start_index = markers[i][0]
        # End at the next marker, or end of text
        end_index = markers[i+1][0] if i + 1 < len(markers) else len(full_text)
        
        chunk_content = full_text[start_index:end_index].strip()
        chunk_type = markers[i][1]
        chunk_title = markers[i][2]

        # Filter out tiny chunks (often misidentified headers)
        if len(chunk_content) < 50:
            continue

        # For "PART" chunks, usually, they just contain the title. 
        # We might want to merge them or just ignore them if they don't have content.
        # But Rules and Schedules are the priority.
        
        # Add context to the chunk text for the LLM
        formatted_chunk = f"[{chunk_type}] {chunk_title}\n\n{chunk_content}"
        chunks.append(formatted_chunk)

    print(f"   ✅ Extracted {len(chunks)} semantic chunks (Rules/Schedules)")
    return chunks


def extract_rules(client: OpenAI, text_chunks: List[str]) -> List[Dict]:
    """Use LLM to extract structured rules from semantic chunks."""
    print("🔄 Extracting academic rules using LLM...")
    
    all_rules = []
    
    # Updated Prompt for Tables and Schedules
    extraction_prompt = """You are an expert legal parser for university academic rules.
Your task is to convert the provided text chunk into a structured JSON object.

The text represents a specific "Rule" or "Schedule" from the student handbook.

INSTRUCTIONS:
1. If the text contains a **Schedule (Table)** (e.g., Grading System, Time Table):
   - Extract the table data accurately. 
   - Representation: Convert the table into a Markdown string inside the 'content_english' field.
   
2. If the text is a **Standard Rule**:
   - Extract the full text.
   - If it refers to "Subrule (1)", ensure that is included.

JSON SCHEMA:
[
  {
    "id": "Generate a unique slug (e.g., 'rule-3-registration', 'fifth-schedule-grading')",
    "article_number": "The Rule number (e.g., '3', '56') or 'Schedule X'",
    "section_title": "The exact title of the Rule or Schedule",
    "content_english": "The full content. Use Markdown tables for Schedules.",
    "category": "One of: Registration, Grading, Examination, Attendance, General, Schedule",
    "keywords": ["relevant", "search", "terms"]
  }
]

Input Text:
---
%TEXT%
---

Return ONLY raw JSON.
"""

    for i, chunk in enumerate(text_chunks):
        print(f"   Processing chunk {i+1}/{len(text_chunks)}...", end=" ")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini", # Use gpt-4o for complex tables if mini fails
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant."},
                    {"role": "user", "content": extraction_prompt.replace("%TEXT%", chunk)}
                ],
                temperature=0,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean Markdown formatting
            result_text = re.sub(r'^```json\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            
            rules = json.loads(result_text)
            all_rules.extend(rules)
            print(f"✅ Extracted {len(rules)} items")
            
        except json.JSONDecodeError:
            print(f"⚠️ JSON Error in chunk {i+1}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return all_rules


# [Reusable functions from original script: generate_embedding, save_results]
def generate_embedding(client: OpenAI, rule: Dict) -> List[float]:
    keywords = rule.get('keywords', [])
    keywords_str = ', '.join(keywords) if keywords else ''
    
    searchable_text = f"""
Rule: {rule.get('section_title', '')}
ID: {rule.get('article_number', 'N/A')}
Category: {rule.get('category', '')}
Keywords: {keywords_str}

Content: {rule.get('content_english', '')}
""".strip()
    
    if len(searchable_text) > 8000:
        searchable_text = searchable_text[:8000]
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=searchable_text
    )
    return response.data[0].embedding

def save_results(rules: List[Dict], embeddings: Dict):
    JSON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    
    with open(EMBEDDINGS_OUTPUT_PATH, "wb") as f:
        pickle.dump(embeddings, f)


def main():
    parser = argparse.ArgumentParser(description="Extract academic rules from PDF")
    parser.add_argument("--skip-embeddings", action="store_true", help="Skip embedding generation")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   Academic Rules Semantic Extraction Pipeline")
    print("=" * 60)
    
    if not PDF_PATH.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        return
    
    client = OpenAI()
    
    # Step 1 & 2: Semantic Text Extraction
    semantic_chunks = extract_text_semantically(PDF_PATH)
    
    if not semantic_chunks:
        print("❌ No chunks found!")
        return

    # Step 3: LLM Extraction
    rules = extract_rules(client, semantic_chunks)
    
    # Step 4: Embeddings
    embeddings = {}
    if not args.skip_embeddings:
        print(f"\n🔄 Generating embeddings...")
        for i, rule in enumerate(rules):
            rule_id = rule.get('id', f'rule-{i}')
            print(f"   Embedding {rule_id}...", end=" ")
            try:
                embedding = generate_embedding(client, rule)
                embeddings[rule_id] = {"rule": rule, "embedding": embedding}
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
    
    # Step 5: Save
    save_results(rules, embeddings)
    print("\n✅ Extraction Complete!")

if __name__ == "__main__":
    main()
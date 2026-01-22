"""
Academic Rules PDF Extraction Script.

Extracts structured JSON from academic_rules.pdf using LLM-based parsing.
Chunks by Article/Section headers rather than pages or fixed character counts.

Usage:
    cd AcademicAdvisor-Chatbot-V3
    python tools/extract_rules.py

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
PDF_PATH = PROJECT_ROOT / "data" / "handbook" / "academic_rules" / "academic_rules.pdf"
JSON_OUTPUT_PATH = PROJECT_ROOT / "data" / "handbook" / "json" / "rules.json"
EMBEDDINGS_OUTPUT_PATH = PROJECT_ROOT / "data" / "handbook" / "embeddings" / "rules_embeddings.pkl"


def extract_text_from_pdf(pdf_path: Path) -> str:
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


def chunk_by_article(raw_text: str) -> List[str]:
    """Split text by article/section headers for better semantic chunking."""
    print("🔍 Detecting article/section boundaries...")
    
    # Common patterns for academic policy documents
    # Matches: "ARTICLE 1", "Article 2:", "PART A", "Section 2.1", "CHAPTER 3"
    section_pattern = re.compile(
        r'(?:^|\n)(?:ARTICLE|Article|PART|Part|SECTION|Section|CHAPTER|Chapter)\s*[\dIVXA-Za-z]+[:\.\s]',
        re.MULTILINE | re.IGNORECASE
    )
    
    matches = list(section_pattern.finditer(raw_text))
    
    if not matches:
        print("   ⚠️ No article/section headers found, using page-based chunks")
        # Fallback: split by page markers
        return [chunk for chunk in raw_text.split("--- Page") if len(chunk.strip()) > 100]
    
    chunks = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        chunk = raw_text[start:end].strip()
        
        # Skip very short chunks
        if len(chunk) > 100:
            chunks.append(chunk)
    
    print(f"   Found {len(chunks)} article/section chunks")
    return chunks


def extract_rules(client: OpenAI, text_chunks: List[str]) -> List[Dict]:
    """Use LLM to extract structured rules from text chunks."""
    print("🔄 Extracting academic rules using LLM...")
    
    all_rules = []
    
    extraction_prompt = """You are extracting academic rules and policies from a Malaysian university handbook.
Extract the rules, regulations, and policies from this text. Return a JSON array of rule entries.

Each rule should have this schema:
{
  "id": "unique string identifier (e.g., 'cgpa-calculation-rule', 'probation-policy')",
  "article_number": "Article/Section number if present, else null",
  "section_title": "Title of this rule/section in English",
  "section_title_malay": "Title in Malay if available, else null",
  "content_english": "The full rule content/description in English",
  "content_malay": "The content in Malay if available, else null",
  "category": "One of: grading, attendance, probation, graduation, appeals, registration, examination, conduct, other",
  "keywords": ["list", "of", "relevant", "search", "keywords"]
}

IMPORTANT: 
- Extract the ACTUAL content of the rules, not summaries
- Include formulas for calculations (like CGPA)
- Preserve important numerical values (credit hours, GPA thresholds, etc.)

Text to extract from:
---
%TEXT%
---

Return ONLY a valid JSON array with no markdown formatting. If no rules found, return [].
"""

    for i, chunk in enumerate(text_chunks):
        print(f"   Processing chunk {i+1}/{len(text_chunks)}...", end=" ")
        
        # Skip chunks that are too short
        if len(chunk) < 150:
            print("⏭️ Skipped (too short)")
            continue
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": extraction_prompt.replace("%TEXT%", chunk[:6000])}
                ],
                temperature=0,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up JSON
            if result_text.startswith("```"):
                result_text = re.sub(r'^```json?\n?', '', result_text)
                result_text = re.sub(r'\n?```$', '', result_text)
            
            rules = json.loads(result_text)
            all_rules.extend(rules)
            print(f"✅ Found {len(rules)} rules")
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Deduplicate rules by id
    seen_ids = set()
    unique_rules = []
    for rule in all_rules:
        rule_id = rule.get("id", "")
        if rule_id and rule_id not in seen_ids:
            seen_ids.add(rule_id)
            unique_rules.append(rule)
        elif not rule_id:
            rule["id"] = f"rule-{len(unique_rules) + 1}"
            unique_rules.append(rule)
    
    print(f"✅ Extracted {len(unique_rules)} unique rules")
    return unique_rules


def generate_embedding(client: OpenAI, rule: Dict) -> List[float]:
    """Generate embedding for an academic rule's searchable content."""
    
    keywords = rule.get('keywords', [])
    keywords_str = ', '.join(keywords) if keywords else ''
    
    searchable_text = f"""
Academic Rule: {rule.get('section_title', '')}
Malay Title: {rule.get('section_title_malay', '')}
Article: {rule.get('article_number', 'N/A')}
Category: {rule.get('category', '')}
Keywords: {keywords_str}

Content (English): {rule.get('content_english', '')}
Content (Malay): {rule.get('content_malay', '')}
""".strip()
    
    # Truncate if too long for embedding
    if len(searchable_text) > 8000:
        searchable_text = searchable_text[:8000]
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=searchable_text
    )
    
    return response.data[0].embedding


def save_results(rules: List[Dict], embeddings: Dict):
    """Save extracted rules to JSON and embeddings to pickle."""
    
    # Ensure directories exist
    JSON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(rules)} rules to: {JSON_OUTPUT_PATH}")
    
    # Save embeddings
    with open(EMBEDDINGS_OUTPUT_PATH, "wb") as f:
        pickle.dump(embeddings, f)
    print(f"💾 Saved embeddings to: {EMBEDDINGS_OUTPUT_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Extract academic rules from PDF")
    parser.add_argument("--skip-embeddings", action="store_true", help="Skip embedding generation")
    parser.add_argument("--review-only", action="store_true", help="Only show extracted rules for manual review")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   Academic Rules Extraction Pipeline")
    print("=" * 60)
    
    if not PDF_PATH.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        return
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Step 1: Extract text from PDF
    raw_text = extract_text_from_pdf(PDF_PATH)
    
    # Step 2: Chunk by article/section
    text_chunks = chunk_by_article(raw_text)
    
    # Step 3: Extract rules using LLM
    rules = extract_rules(client, text_chunks)
    
    if not rules:
        print("❌ No academic rules found!")
        return
    
    # Step 4: Manual review step
    print("\n" + "=" * 60)
    print("   📋 MANUAL REVIEW - Extracted Rules Summary")
    print("=" * 60)
    for i, rule in enumerate(rules[:10]):  # Show first 10
        print(f"\n{i+1}. {rule.get('section_title', 'Unknown')}")
        print(f"   Article: {rule.get('article_number', 'N/A')}")
        print(f"   Category: {rule.get('category', 'N/A')}")
        # Show first 100 chars of content
        content = rule.get('content_english', '')[:100]
        if content:
            print(f"   Content: {content}...")
    
    if len(rules) > 10:
        print(f"\n   ... and {len(rules) - 10} more rules")
    
    if args.review_only:
        print("\n⏸️  Review mode: exiting without saving.")
        print(f"   Run again without --review-only to generate output files.")
        return
    
    # Step 5: Generate embeddings
    embeddings = {}
    if not args.skip_embeddings:
        print(f"\n🔄 Generating embeddings...")
        for i, rule in enumerate(rules):
            rule_id = rule.get('id', f'rule-{i}')
            print(f"   [{i+1}/{len(rules)}] Embedding {rule_id}...", end=" ")
            try:
                embedding = generate_embedding(client, rule)
                embeddings[rule_id] = {
                    "rule": rule,
                    "embedding": embedding
                }
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
    
    # Step 6: Save results
    print()
    save_results(rules, embeddings)
    
    print("\n" + "=" * 60)
    print(f"   ✅ Pipeline Complete!")
    print(f"   Rules extracted: {len(rules)}")
    print(f"   Embeddings generated: {len(embeddings)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

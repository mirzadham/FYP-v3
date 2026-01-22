"""
Advanced Academic Calendar Extractor (V2).

Target PDF: UPM Academic Calendar 2025/2026
Key Challenges Solved:
1. Parallel Columns: Extracts 'Activities' and 'Public Holidays' as separate event streams
   even when they appear on the same row.
2. Layout Variations: Handles the "Academic" table (Pages 1,3,5) and "Administrative" 
   table (Pages 2,4) differently.
3. Error Correction: Detects the typo on Page 4 where the header says "SEMESTER PERTAMA"
   but the dates indicate "SEMESTER KEDUA".
"""

import os
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
PDF_PATH = PROJECT_ROOT / "data" / "handbook" / "academic_calendar" / "academic_calendar.pdf"
JSON_OUTPUT_PATH = PROJECT_ROOT / "data" / "handbook" / "json" / "calendar.json"
EMBEDDINGS_OUTPUT_PATH = PROJECT_ROOT / "data" / "handbook" / "embeddings" / "calendar_embeddings.pkl"


def extract_events_from_page(client: OpenAI, page_text: str, page_num: int) -> List[Dict]:
    """
    Extracts structured events using a prompt specifically designed for UPM's dual-column layout.
    """
    print(f"   Processing Page {page_num + 1}...", end=" ")

    # Custom prompt that handles the specific visual layout of this PDF
    extraction_prompt = f"""
You are an expert data parser for a university calendar (UPM). 
Analyze the text from Page {page_num + 1} and extract a JSON array of events.

### CRITICAL PARSING RULES:
1. **Dual Column Layout (Pages 1, 3, 5)**: 
   - These pages have "Activities" on the left and "Public Holidays" on the right.
   - Treat them as SEPARATE events. 
   - Example: If a row has "Lecture Week 5" on the left and "Deepavali" on the right, create TWO objects: one for the lecture range, one for the holiday.

2. **Semester Inference & Correction**:
   - Determine the semester from the page header.
   - **CORRECTION RULE**: If the header says "SEMESTER PERTAMA" but the dates are in March-August 2026, output "Semester II" (The PDF has a known typo on Page 4).

3. **Dates**:
   - Convert all dates to `YYYY-MM-DD` format.
   - Handle ranges (e.g., "13.10.2025 - 19.10.2025").

### JSON Schema:
Return ONLY a JSON array of objects with this structure:
{{
  "id": "slug-id (e.g., 'sem1-lecture-wk2' or 'sem1-holiday-deepavali')",
  "event_name": "Name in English (e.g., 'Final Examination', 'Deepavali')",
  "event_name_malay": "Name in Malay (e.g., 'Peperiksaan Akhir')",
  "semester": "Semester I, Semester II, or Semester III",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD (null if same day)",
  "category": "Choose: 'Academic', 'Administrative', 'Holiday', 'Exam'",
  "remarks": "Any notes (e.g., 'Online Class', '7 Weeks')"
}}

### Raw Page Text:
---
{page_text}
---
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a logical data cleaning assistant."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0,
            max_tokens=4000
        )

        result_text = response.choices[0].message.content.strip()

        # Sanitize JSON output
        if result_text.startswith("```"):
            result_text = re.sub(r'^```json?\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)

        events = json.loads(result_text)
        print(f"✅ Found {len(events)} events")
        return events

    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse error on page {page_num + 1}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error on page {page_num + 1}: {e}")
        return []


def generate_embedding(client: OpenAI, event: Dict) -> List[float]:
    """Generates a search-optimized embedding."""
    
    # Structure text to favor questions like "When is the final exam?"
    searchable_text = f"""
Event: {event.get('event_name', '')}
Malay: {event.get('event_name_malay', '')}
Semester: {event.get('semester', 'General')}
Date: {event.get('start_date', '')}
Category: {event.get('category', '')}
Remarks: {event.get('remarks', '')}
""".strip()

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=searchable_text
    )
    return response.data[0].embedding


def save_results(events: List[Dict], embeddings: Dict):
    """Saves output to disk."""
    JSON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(events)} events to: {JSON_OUTPUT_PATH}")

    with open(EMBEDDINGS_OUTPUT_PATH, "wb") as f:
        pickle.dump(embeddings, f)
    print(f"💾 Saved embeddings to: {EMBEDDINGS_OUTPUT_PATH}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-embeddings", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("   Academic Calendar Extractor V2 (Smart Parsing)")
    print("=" * 60)

    if not PDF_PATH.exists():
        print(f"❌ PDF not found at: {PDF_PATH}")
        return

    client = OpenAI()
    
    # 1. Open PDF
    doc = pymupdf.open(PDF_PATH)
    total_pages = doc.page_count
    print(f"📄 Processing {total_pages} pages...")

    all_events = []

    # 2. Process Page-by-Page
    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        # sort=True is vital for tables to keep columns somewhat together
        raw_text = page.get_text("text", sort=True)
        
        events = extract_events_from_page(client, raw_text, page_num)
        all_events.extend(events)

    doc.close()

    if not all_events:
        print("❌ No events extracted.")
        return

    # 3. Embeddings & Save
    embeddings = {}
    if not args.skip_embeddings:
        print(f"\n🔄 Generating embeddings for {len(all_events)} events...")
        for i, event in enumerate(all_events):
            # Generate a unique key if ID is missing or duplicate
            event_id = event.get('id')
            if not event_id or event_id in embeddings:
                event_id = f"evt-{i}-{event.get('start_date', 'nodate')}"
                event['id'] = event_id
            
            try:
                embedding = generate_embedding(client, event)
                embeddings[event_id] = {"event": event, "embedding": embedding}
            except Exception as e:
                print(f"   ❌ Failed to embed {event_id}: {e}")
        print("✅ Embeddings complete.")

    save_results(all_events, embeddings)
    print("\n✅ Pipeline Complete.")

if __name__ == "__main__":
    main()
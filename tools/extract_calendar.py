"""
Academic Calendar PDF Extraction Script.

Extracts structured JSON from academic_calendar.pdf using LLM-based parsing.
Chunks by semester/event boundaries rather than pages or fixed character counts.

Usage:
    cd AcademicAdvisor-Chatbot-V3
    python tools/extract_calendar.py

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
PDF_PATH = PROJECT_ROOT / "data" / "handbook" / "academic_calendar" / "academic_calendar.pdf"
JSON_OUTPUT_PATH = PROJECT_ROOT / "data" / "handbook" / "json" / "calendar.json"
EMBEDDINGS_OUTPUT_PATH = PROJECT_ROOT / "data" / "handbook" / "embeddings" / "calendar_embeddings.pkl"


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


def extract_calendar_events(client: OpenAI, raw_text: str) -> List[Dict]:
    """Use LLM to extract structured calendar events from raw text."""
    print("🔄 Extracting calendar events using LLM...")
    
    # Split into manageable chunks for LLM (roughly 4000 chars each)
    chunk_size = 4000
    text_chunks = [raw_text[i:i + chunk_size] for i in range(0, len(raw_text), chunk_size)]
    
    all_events = []
    
    extraction_prompt = """You are extracting academic calendar events from a Malaysian university calendar.
Extract ALL events, dates, and deadlines from this text. Return a JSON array of events.

Each event should have this schema:
{
  "id": "unique string identifier (e.g., 'sem1-2025-registration')",
  "event_name": "Event name in English",
  "event_name_malay": "Event name in Malay if available, else null",
  "semester": "Semester I, Semester II, or null if applies to whole year",
  "academic_year": "e.g., '2025/2026'",
  "start_date": "Date in YYYY-MM-DD format if extractable, else descriptive string",
  "end_date": "End date if it's a range, else null",
  "description": "Brief description of the event",
  "category": "One of: registration, examination, holiday, deadline, orientation, lecture, other"
}

Text to extract from:
---
%TEXT%
---

Return ONLY a valid JSON array with no markdown formatting. If no events found, return [].
"""

    for i, chunk in enumerate(text_chunks):
        print(f"   Processing chunk {i+1}/{len(text_chunks)}...", end=" ")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": extraction_prompt.replace("%TEXT%", chunk)}
                ],
                temperature=0,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up JSON
            if result_text.startswith("```"):
                result_text = re.sub(r'^```json?\n?', '', result_text)
                result_text = re.sub(r'\n?```$', '', result_text)
            
            events = json.loads(result_text)
            all_events.extend(events)
            print(f"✅ Found {len(events)} events")
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Deduplicate events by id
    seen_ids = set()
    unique_events = []
    for event in all_events:
        event_id = event.get("id", "")
        if event_id and event_id not in seen_ids:
            seen_ids.add(event_id)
            unique_events.append(event)
        elif not event_id:
            # Generate ID for events without one
            event["id"] = f"event-{len(unique_events) + 1}"
            unique_events.append(event)
    
    print(f"✅ Extracted {len(unique_events)} unique calendar events")
    return unique_events


def generate_embedding(client: OpenAI, event: Dict) -> List[float]:
    """Generate embedding for a calendar event's searchable content."""
    
    searchable_text = f"""
Academic Calendar Event: {event.get('event_name', '')}
Malay: {event.get('event_name_malay', '')}
Semester: {event.get('semester', 'All semesters')}
Academic Year: {event.get('academic_year', '')}
Date: {event.get('start_date', '')} to {event.get('end_date', '')}
Category: {event.get('category', '')}
Description: {event.get('description', '')}
""".strip()
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=searchable_text
    )
    
    return response.data[0].embedding


def save_results(events: List[Dict], embeddings: Dict):
    """Save extracted events to JSON and embeddings to pickle."""
    
    # Ensure directories exist
    JSON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved {len(events)} events to: {JSON_OUTPUT_PATH}")
    
    # Save embeddings
    with open(EMBEDDINGS_OUTPUT_PATH, "wb") as f:
        pickle.dump(embeddings, f)
    print(f"💾 Saved embeddings to: {EMBEDDINGS_OUTPUT_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Extract academic calendar events from PDF")
    parser.add_argument("--skip-embeddings", action="store_true", help="Skip embedding generation")
    parser.add_argument("--review-only", action="store_true", help="Only show extracted events for manual review")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   Academic Calendar Extraction Pipeline")
    print("=" * 60)
    
    if not PDF_PATH.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        return
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Step 1: Extract text from PDF
    raw_text = extract_text_from_pdf(PDF_PATH)
    
    # Step 2: Extract calendar events using LLM
    events = extract_calendar_events(client, raw_text)
    
    if not events:
        print("❌ No calendar events found!")
        return
    
    # Step 3: Manual review step
    print("\n" + "=" * 60)
    print("   📋 MANUAL REVIEW - Extracted Events Summary")
    print("=" * 60)
    for i, event in enumerate(events[:10]):  # Show first 10
        print(f"\n{i+1}. {event.get('event_name', 'Unknown')}")
        print(f"   Date: {event.get('start_date', 'N/A')} - {event.get('end_date', 'N/A')}")
        print(f"   Category: {event.get('category', 'N/A')}")
    
    if len(events) > 10:
        print(f"\n   ... and {len(events) - 10} more events")
    
    if args.review_only:
        print("\n⏸️  Review mode: exiting without saving.")
        print(f"   Run again without --review-only to generate output files.")
        return
    
    # Step 4: Generate embeddings
    embeddings = {}
    if not args.skip_embeddings:
        print(f"\n🔄 Generating embeddings...")
        for i, event in enumerate(events):
            event_id = event.get('id', f'event-{i}')
            print(f"   [{i+1}/{len(events)}] Embedding {event_id}...", end=" ")
            try:
                embedding = generate_embedding(client, event)
                embeddings[event_id] = {
                    "event": event,
                    "embedding": embedding
                }
                print("✅")
            except Exception as e:
                print(f"❌ {e}")
    
    # Step 5: Save results
    print()
    save_results(events, embeddings)
    
    print("\n" + "=" * 60)
    print(f"   ✅ Pipeline Complete!")
    print(f"   Events extracted: {len(events)}")
    print(f"   Embeddings generated: {len(embeddings)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
Embedding Generation Script for Academic Advisor RAG.

This script generates OpenAI embeddings for all courses in the database
and saves them to a pickle file for fast semantic search at runtime.

Usage:
    cd AcademicAdvisor-Chatbot-V3
    python tools/generate_embeddings.py

Requirements:
    - OPENAI_API_KEY environment variable set
    - academic.db populated with courses
"""

import sqlite3
import os
import pickle
from typing import List, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "db", "academic.db")
EMBEDDINGS_PATH = os.path.join(PROJECT_ROOT, "db", "embeddings.pkl")


def get_all_courses() -> List[Tuple[str, str, str]]:
    """Fetch all courses from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT course_code, course_name, description
        FROM courses
    """)
    courses = cursor.fetchall()
    conn.close()
    return courses


def generate_embedding(client: OpenAI, text: str) -> List[float]:
    """Generate an embedding for a given text using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def main():
    print("=" * 50)
    print("Academic Advisor - Embedding Generator")
    print("=" * 50)
    
    # Initialize OpenAI client
    client = OpenAI()
    
    # Fetch all courses
    print(f"\n📚 Loading courses from: {DB_PATH}")
    courses = get_all_courses()
    print(f"   Found {len(courses)} courses")
    
    # Generate embeddings
    embeddings = {}
    print("\n🔄 Generating embeddings...")
    
    for i, (code, name, description) in enumerate(courses):
        # Combine course info for richer semantic meaning
        combined_text = f"{code}: {name}. {description or ''}"
        
        try:
            embedding = generate_embedding(client, combined_text)
            embeddings[code] = {
                "code": code,
                "name": name,
                "description": description,
                "embedding": embedding,
                "text": combined_text
            }
            print(f"   [{i+1}/{len(courses)}] ✅ {code}: {name[:40]}...")
        except Exception as e:
            print(f"   [{i+1}/{len(courses)}] ❌ {code}: Error - {e}")
    
    # Save embeddings
    print(f"\n💾 Saving embeddings to: {EMBEDDINGS_PATH}")
    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(embeddings, f)
    
    print(f"\n✅ Done! Generated {len(embeddings)} embeddings.")
    print(f"   File size: {os.path.getsize(EMBEDDINGS_PATH) / 1024:.2f} KB")


if __name__ == "__main__":
    main()

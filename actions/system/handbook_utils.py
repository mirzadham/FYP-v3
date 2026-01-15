"""
Handbook utilities for Academic Advisor Chatbot.

Provides semantic search and course lookup using extracted handbook data.
Replaces SQLite database with JSON + embeddings from faculty handbooks.
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Any
from functools import lru_cache
from openai import OpenAI

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
HANDBOOK_JSON_DIR = PROJECT_ROOT / "data" / "handbook" / "json"
HANDBOOK_EMBEDDINGS_DIR = PROJECT_ROOT / "data" / "handbook" / "embeddings"


class HandbookStore:
    """
    Singleton class for loading and caching handbook data.
    
    Loads all JSON course files and embeddings on first access,
    then caches them for fast subsequent lookups.
    """
    
    _instance = None
    _courses: Dict[str, Dict] = {}  # {course_code: course_data}
    _embeddings: Dict[str, List[float]] = {}  # {course_code: embedding_vector}
    _loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_data(self):
        """Load all JSON and embedding files from handbook directories."""
        if self._loaded:
            return
        
        # Load all JSON files
        if HANDBOOK_JSON_DIR.exists():
            for json_file in HANDBOOK_JSON_DIR.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        courses = json.load(f)
                        for course in courses:
                            code = course.get("course_code")
                            if code:
                                # If duplicate, keep the one with more data
                                if code not in self._courses or \
                                   len(str(course)) > len(str(self._courses.get(code, {}))):
                                    self._courses[code] = course
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
        
        # Load all embedding files
        if HANDBOOK_EMBEDDINGS_DIR.exists():
            for pkl_file in HANDBOOK_EMBEDDINGS_DIR.glob("*_embeddings.pkl"):
                try:
                    with open(pkl_file, "rb") as f:
                        embeddings = pickle.load(f)
                        for code, data in embeddings.items():
                            if code not in self._embeddings:
                                self._embeddings[code] = data.get("embedding", [])
                except Exception as e:
                    print(f"Error loading {pkl_file}: {e}")
        
        self._loaded = True
        print(f"📚 HandbookStore: Loaded {len(self._courses)} courses, {len(self._embeddings)} embeddings")
    
    def get_all_courses(self) -> Dict[str, Dict]:
        """Get all courses as a dict keyed by course code."""
        self._load_data()
        return self._courses
    
    def get_all_embeddings(self) -> Dict[str, List[float]]:
        """Get all embeddings as a dict keyed by course code."""
        self._load_data()
        return self._embeddings
    
    def get_course(self, course_code: str) -> Optional[Dict]:
        """Get a specific course by code."""
        self._load_data()
        # Try exact match first
        code = course_code.upper().strip()
        if code in self._courses:
            return self._courses[code]
        # Try fuzzy match (without spaces/dashes)
        normalized = code.replace(" ", "").replace("-", "")
        for key in self._courses:
            if key.replace(" ", "").replace("-", "") == normalized:
                return self._courses[key]
        return None
    
    def reload(self):
        """Force reload all data (useful after new extractions)."""
        self._courses = {}
        self._embeddings = {}
        self._loaded = False
        self._load_data()


# Global store instance
_store = HandbookStore()


def get_course_by_code(course_code: str) -> Optional[Dict]:
    """
    Get course details by course code.
    
    Args:
        course_code: The course code to look up (e.g., "CCS3001")
        
    Returns:
        Course dict with keys: course_code, course_name_english, course_name_malay,
        credits, prerequisites, description_english, description_malay, 
        department, faculty
    """
    return _store.get_course(course_code)


def get_prerequisites_for_course(course_code: str) -> List[str]:
    """
    Get prerequisites for a course.
    
    Args:
        course_code: The course code to look up
        
    Returns:
        List of prerequisite course codes, or empty list if none
    """
    course = _store.get_course(course_code)
    if course:
        prereqs = course.get("prerequisites", [])
        if prereqs and isinstance(prereqs, list):
            return [p for p in prereqs if p]  # Filter out None/empty
    return []


def semantic_search(query: str, top_k: int = 5) -> List[Dict]:
    """
    Perform semantic search across all course embeddings.
    
    Args:
        query: User's natural language query
        top_k: Number of top results to return
        
    Returns:
        List of course dicts, ordered by relevance
    """
    embeddings = _store.get_all_embeddings()
    courses = _store.get_all_courses()
    
    if not embeddings:
        print("⚠️ No embeddings loaded for semantic search")
        return []
    
    try:
        # Generate embedding for query
        client = OpenAI()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = np.array(response.data[0].embedding)
        
        # Calculate cosine similarity with all embeddings
        similarities = []
        for code, embedding in embeddings.items():
            if embedding and code in courses:
                emb_array = np.array(embedding)
                # Cosine similarity
                similarity = np.dot(query_embedding, emb_array) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(emb_array)
                )
                similarities.append((code, similarity, courses[code]))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [item[2] for item in similarities[:top_k]]
        
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []


def get_context_for_rag(query: str, top_k: int = 5) -> str:
    """
    Get formatted context string for RAG prompts.
    
    Args:
        query: User's query
        top_k: Number of courses to include
        
    Returns:
        Formatted string with relevant course information
    """
    results = semantic_search(query, top_k)
    
    if not results:
        return "No relevant course information found."
    
    context_parts = []
    for course in results:
        code = course.get("course_code", "Unknown")
        name_en = course.get("course_name_english", "")
        name_my = course.get("course_name_malay", "")
        credits = course.get("credits", "")
        desc_en = course.get("description_english", "")[:300] if course.get("description_english") else ""
        prereqs = course.get("prerequisites", [])
        faculty = course.get("faculty", "")
        
        part = f"**{code}**: {name_en or name_my}"
        if credits:
            part += f" ({credits})"
        if faculty:
            part += f"\nFaculty: {faculty}"
        if prereqs:
            part += f"\nPrerequisites: {', '.join(prereqs)}"
        if desc_en:
            part += f"\n{desc_en}..."
        
        context_parts.append(part)
    
    return "\n\n".join(context_parts)


def get_course_count() -> int:
    """Get total number of courses loaded."""
    return len(_store.get_all_courses())


def get_embedding_count() -> int:
    """Get total number of embeddings loaded."""
    return len(_store.get_all_embeddings())

"""
Handbook utilities for Academic Advisor Chatbot.

Provides semantic search and lookup using extracted handbook data.
Supports multiple domains: courses, calendar, and academic rules.
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Literal
from functools import lru_cache
from openai import OpenAI

# Type alias for domain
DomainType = Literal["courses", "calendar", "rules", "all"]

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
HANDBOOK_DATA_DIR = PROJECT_ROOT / "data" / "handbook"

# Course paths (consolidated structure)
COURSES_JSON_DIR = HANDBOOK_DATA_DIR / "json" / "courses"
COURSES_EMBEDDINGS_DIR = HANDBOOK_DATA_DIR / "embeddings" / "courses"

# Calendar paths
CALENDAR_JSON_PATH = HANDBOOK_DATA_DIR / "json" / "calendar.json"
CALENDAR_EMBEDDINGS_PATH = HANDBOOK_DATA_DIR / "embeddings" / "calendar_embeddings.pkl"

# Rules paths
RULES_JSON_PATH = HANDBOOK_DATA_DIR / "json" / "rules.json"
RULES_EMBEDDINGS_PATH = HANDBOOK_DATA_DIR / "embeddings" / "rules_embeddings.pkl"


class HandbookStore:
    """
    Singleton class for loading and caching handbook data.
    
    Supports three domains:
    - courses: Course information from faculty handbooks
    - calendar: Academic calendar events
    - rules: Academic policies and regulations
    
    Loads all data on first access, then caches for fast lookups.
    Thread-safe singleton pattern for Rasa action server.
    """
    
    _instance = None
    
    # Course data
    _courses: Dict[str, Dict] = {}
    _course_embeddings: Dict[str, List[float]] = {}
    
    # Calendar data
    _calendar: Dict[str, Dict] = {}
    _calendar_embeddings: Dict[str, List[float]] = {}
    
    # Rules data
    _rules: Dict[str, Dict] = {}
    _rules_embeddings: Dict[str, List[float]] = {}
    
    _loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_data(self):
        """Load all JSON and embedding files from handbook directories."""
        if self._loaded:
            return
        
        self._load_courses()
        self._load_calendar()
        self._load_rules()
        
        self._loaded = True
        print(f"📚 HandbookStore: Loaded {len(self._courses)} courses, "
              f"{len(self._calendar)} calendar events, {len(self._rules)} rules")
    
    def _load_courses(self):
        """Load course data from JSON and embeddings."""
        # Load from consolidated courses directory
        if COURSES_JSON_DIR.exists():
            for json_file in COURSES_JSON_DIR.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        courses = json.load(f)
                        for course in courses:
                            code = course.get("course_code")
                            if code:
                                if code not in self._courses or \
                                   len(str(course)) > len(str(self._courses.get(code, {}))):
                                    self._courses[code] = course
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
        
        # Load course embeddings
        if COURSES_EMBEDDINGS_DIR.exists():
            for pkl_file in COURSES_EMBEDDINGS_DIR.glob("*_embeddings.pkl"):
                try:
                    with open(pkl_file, "rb") as f:
                        embeddings = pickle.load(f)
                        for code, data in embeddings.items():
                            if code not in self._course_embeddings:
                                self._course_embeddings[code] = data.get("embedding", [])
                except Exception as e:
                    print(f"Error loading {pkl_file}: {e}")
    
    def _load_calendar(self):
        """Load calendar data from JSON and embeddings."""
        if CALENDAR_JSON_PATH.exists():
            try:
                with open(CALENDAR_JSON_PATH, "r", encoding="utf-8") as f:
                    events = json.load(f)
                    for event in events:
                        event_id = event.get("id")
                        if event_id:
                            self._calendar[event_id] = event
            except Exception as e:
                print(f"Error loading calendar.json: {e}")
        
        if CALENDAR_EMBEDDINGS_PATH.exists():
            try:
                with open(CALENDAR_EMBEDDINGS_PATH, "rb") as f:
                    embeddings = pickle.load(f)
                    for event_id, data in embeddings.items():
                        self._calendar_embeddings[event_id] = data.get("embedding", [])
            except Exception as e:
                print(f"Error loading calendar embeddings: {e}")
    
    def _load_rules(self):
        """Load rules data from JSON and embeddings."""
        if RULES_JSON_PATH.exists():
            try:
                with open(RULES_JSON_PATH, "r", encoding="utf-8") as f:
                    rules = json.load(f)
                    for rule in rules:
                        rule_id = rule.get("id")
                        if rule_id:
                            self._rules[rule_id] = rule
            except Exception as e:
                print(f"Error loading rules.json: {e}")
        
        if RULES_EMBEDDINGS_PATH.exists():
            try:
                with open(RULES_EMBEDDINGS_PATH, "rb") as f:
                    embeddings = pickle.load(f)
                    for rule_id, data in embeddings.items():
                        self._rules_embeddings[rule_id] = data.get("embedding", [])
            except Exception as e:
                print(f"Error loading rules embeddings: {e}")
    
    # === Course accessors ===
    def get_all_courses(self) -> Dict[str, Dict]:
        """Get all courses as a dict keyed by course code."""
        self._load_data()
        return self._courses
    
    def get_course_embeddings(self) -> Dict[str, List[float]]:
        """Get all course embeddings."""
        self._load_data()
        return self._course_embeddings
    
    def get_course(self, course_code: str) -> Optional[Dict]:
        """Get a specific course by code."""
        self._load_data()
        code = course_code.upper().strip()
        if code in self._courses:
            return self._courses[code]
        # Fuzzy match
        normalized = code.replace(" ", "").replace("-", "")
        for key in self._courses:
            if key.replace(" ", "").replace("-", "") == normalized:
                return self._courses[key]
        return None
    
    # === Calendar accessors ===
    def get_all_calendar(self) -> Dict[str, Dict]:
        """Get all calendar events as a dict keyed by event ID."""
        self._load_data()
        return self._calendar
    
    def get_calendar_embeddings(self) -> Dict[str, List[float]]:
        """Get all calendar embeddings."""
        self._load_data()
        return self._calendar_embeddings
    
    # === Rules accessors ===
    def get_all_rules(self) -> Dict[str, Dict]:
        """Get all rules as a dict keyed by rule ID."""
        self._load_data()
        return self._rules
    
    def get_rules_embeddings(self) -> Dict[str, List[float]]:
        """Get all rules embeddings."""
        self._load_data()
        return self._rules_embeddings
    
    # === Legacy compatibility ===
    def get_all_embeddings(self) -> Dict[str, List[float]]:
        """Legacy: Get course embeddings (for backward compatibility)."""
        return self.get_course_embeddings()
    
    def reload(self):
        """Force reload all data (useful after new extractions)."""
        self._courses = {}
        self._course_embeddings = {}
        self._calendar = {}
        self._calendar_embeddings = {}
        self._rules = {}
        self._rules_embeddings = {}
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
            return [p for p in prereqs if p]
    return []


def _compute_similarity(query_embedding: np.ndarray, embeddings: Dict[str, List[float]], 
                        data: Dict[str, Dict]) -> List[tuple]:
    """Compute cosine similarity between query and all embeddings."""
    similarities = []
    for item_id, embedding in embeddings.items():
        if embedding and item_id in data:
            emb_array = np.array(embedding)
            similarity = np.dot(query_embedding, emb_array) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb_array)
            )
            similarities.append((item_id, similarity, data[item_id]))
    return similarities


def semantic_search(query: str, top_k: int = 5, domain: DomainType = "all") -> List[Dict]:
    """
    Perform semantic search across handbook embeddings.
    
    Args:
        query: User's natural language query
        top_k: Number of top results to return
        domain: Which domain to search - "courses", "calendar", "rules", or "all"
        
    Returns:
        List of matching items, ordered by relevance
    """
    # Collect embeddings and data based on domain
    search_targets = []
    
    if domain in ("courses", "all"):
        search_targets.append((
            _store.get_course_embeddings(),
            _store.get_all_courses(),
            "course"
        ))
    
    if domain in ("calendar", "all"):
        search_targets.append((
            _store.get_calendar_embeddings(),
            _store.get_all_calendar(),
            "calendar"
        ))
    
    if domain in ("rules", "all"):
        search_targets.append((
            _store.get_rules_embeddings(),
            _store.get_all_rules(),
            "rule"
        ))
    
    # Check if any embeddings exist
    has_embeddings = any(embeddings for embeddings, _, _ in search_targets)
    if not has_embeddings:
        print(f"⚠️ No embeddings loaded for domain '{domain}'")
        return []
    
    try:
        # Generate embedding for query
        client = OpenAI()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = np.array(response.data[0].embedding)
        
        # Calculate similarities across all target domains
        all_similarities = []
        for embeddings, data, item_type in search_targets:
            sims = _compute_similarity(query_embedding, embeddings, data)
            # Add item type to each result
            for item_id, sim, item_data in sims:
                item_with_type = dict(item_data)
                item_with_type["_domain"] = item_type
                all_similarities.append((item_id, sim, item_with_type))
        
        # Sort by similarity and return top_k
        all_similarities.sort(key=lambda x: x[1], reverse=True)
        return [item[2] for item in all_similarities[:top_k]]
        
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []


def get_context_for_rag(query: str, top_k: int = 5, domain: DomainType = "all") -> str:
    """
    Get formatted context string for RAG prompts.
    
    Args:
        query: User's query
        top_k: Number of items to include
        domain: Which domain to search
        
    Returns:
        Formatted string with relevant information
    """
    results = semantic_search(query, top_k, domain)
    
    if not results:
        return "No relevant information found in the knowledge base."
    
    context_parts = []
    
    for item in results:
        item_type = item.get("_domain", "unknown")
        
        if item_type == "course":
            context_parts.append(_format_course_context(item))
        elif item_type == "calendar":
            context_parts.append(_format_calendar_context(item))
        elif item_type == "rule":
            context_parts.append(_format_rules_context(item))
    
    return "\n\n".join(context_parts)


def _format_course_context(course: Dict) -> str:
    """Format a course for RAG context."""
    code = course.get("course_code", "Unknown")
    name_en = course.get("course_name_english", "")
    name_my = course.get("course_name_malay", "")
    credits = course.get("credits", "")
    desc_en = course.get("description_english", "")[:300] if course.get("description_english") else ""
    prereqs = course.get("prerequisites", [])
    faculty = course.get("faculty", "")
    
    part = f"[COURSE] {code}: {name_en or name_my}"
    if credits:
        part += f" ({credits})"
    if faculty:
        part += f"\nFaculty: {faculty}"
    if prereqs:
        part += f"\nPrerequisites: {', '.join(prereqs)}"
    if desc_en:
        part += f"\n{desc_en}..."
    
    return part


def _format_calendar_context(event: Dict) -> str:
    """Format a calendar event for RAG context."""
    name = event.get("event_name", "Unknown Event")
    name_my = event.get("event_name_malay", "")
    start = event.get("start_date", "")
    end = event.get("end_date", "")
    semester = event.get("semester", "")
    academic_year = event.get("academic_year", "")
    desc = event.get("description", "")
    
    part = f"[CALENDAR] {name}"
    if name_my:
        part += f" / {name_my}"
    if start:
        date_str = start
        if end and end != start:
            date_str += f" to {end}"
        part += f"\nDate: {date_str}"
    if semester:
        part += f"\nSemester: {semester}"
    if academic_year:
        part += f"\nAcademic Year: {academic_year}"
    if desc:
        part += f"\n{desc[:200]}..."
    
    return part


def _format_rules_context(rule: Dict) -> str:
    """Format an academic rule for RAG context."""
    title = rule.get("section_title", "Unknown Rule")
    title_my = rule.get("section_title_malay", "")
    article = rule.get("article_number", "")
    content = rule.get("content_english", "")[:500] if rule.get("content_english") else ""
    category = rule.get("category", "")
    
    part = f"[RULE] {title}"
    if title_my:
        part += f" / {title_my}"
    if article:
        part += f"\nArticle: {article}"
    if category:
        part += f"\nCategory: {category}"
    if content:
        part += f"\n{content}..."
    
    return part


# === Utility functions ===

def get_course_count() -> int:
    """Get total number of courses loaded."""
    return len(_store.get_all_courses())


def get_embedding_count() -> int:
    """Get total number of course embeddings loaded."""
    return len(_store.get_course_embeddings())


def get_calendar_count() -> int:
    """Get total number of calendar events loaded."""
    return len(_store.get_all_calendar())


def get_rules_count() -> int:
    """Get total number of rules loaded."""
    return len(_store.get_all_rules())

"""
Database utilities for Academic Advisor Chatbot.
Shared database connection and query helpers.

Database Schema:
- courses: course_code (PK), course_name, credit_hours, description
- prerequisites: course_code, prereq_code
"""

import sqlite3
import os
from typing import Optional


# Database path - relative to the project root
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "academic.db")


def get_db_connection() -> sqlite3.Connection:
    """
    Create a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Active database connection
    """
    return sqlite3.connect(DB_PATH)


def get_prerequisites_for_course(course_code: str, cursor: sqlite3.Cursor) -> Optional[str]:
    """
    Query prerequisites for a given course code.
    
    Args:
        course_code: The course code to check prerequisites for
        cursor: Active database cursor
        
    Returns:
        Formatted string of prerequisites or None if no prerequisites exist
    """
    cursor.execute("""
        SELECT c.course_name, p.prereq_code
        FROM prerequisites p
        JOIN courses c ON c.course_code = p.prereq_code
        WHERE UPPER(p.course_code) = ?
    """, (course_code.upper(),))
    
    prereqs = cursor.fetchall()
    
    if prereqs:
        prereq_list = [f"• {code}: {name}" for name, code in prereqs]
        return "\n".join(prereq_list)
    return None

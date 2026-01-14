"""
Tests for database utility functions.

Tests:
- get_db_connection()
- get_prerequisites_for_course()
- DB_PATH validation
"""

import pytest
import sqlite3
import os

from actions.system.db_utils import (
    get_db_connection,
    get_prerequisites_for_course,
    DB_PATH,
)


class TestDbPath:
    """Tests for database path configuration."""

    def test_db_path_exists(self):
        """Database file exists at expected path."""
        assert os.path.exists(DB_PATH), f"Database not found at {DB_PATH}"

    def test_db_path_is_sqlite_file(self):
        """Database path points to a valid file."""
        assert os.path.isfile(DB_PATH), f"{DB_PATH} is not a file"


class TestGetDbConnection:
    """Tests for get_db_connection() function."""

    def test_returns_valid_connection(self):
        """UT-017: get_db_connection() returns valid SQLite connection."""
        conn = get_db_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_connection_can_execute_query(self):
        """Connection can execute basic query."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        assert result == (1,)

    def test_connection_can_access_courses_table(self):
        """Connection can access courses table."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM courses")
        result = cursor.fetchone()
        conn.close()
        
        assert result[0] >= 0  # At least 0 courses


class TestGetPrerequisitesForCourse:
    """Tests for get_prerequisites_for_course() function."""

    def test_course_with_prerequisites(self):
        """UT-018: Returns formatted prerequisite list for course with prereqs."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find a course with prerequisites
        cursor.execute("SELECT DISTINCT course_code FROM prerequisites LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            course_code = result[0]
            prereqs = get_prerequisites_for_course(course_code, cursor)
            
            assert prereqs is not None
            assert isinstance(prereqs, str)
            assert "•" in prereqs  # Check formatting
        
        conn.close()

    def test_course_without_prerequisites(self):
        """UT-019: Returns None for course without prerequisites."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find a course without prerequisites
        cursor.execute("""
            SELECT c.course_code 
            FROM courses c 
            LEFT JOIN prerequisites p ON c.course_code = p.course_code 
            WHERE p.course_code IS NULL 
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            course_code = result[0]
            prereqs = get_prerequisites_for_course(course_code, cursor)
            assert prereqs is None
        
        conn.close()

    def test_nonexistent_course(self):
        """Returns None for non-existent course."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        prereqs = get_prerequisites_for_course("INVALID999", cursor)
        assert prereqs is None
        
        conn.close()

    def test_case_insensitive_lookup(self):
        """Lookup is case-insensitive."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find a course with prerequisites
        cursor.execute("SELECT DISTINCT course_code FROM prerequisites LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            course_code = result[0]
            lowercase_code = course_code.lower()
            
            prereqs_upper = get_prerequisites_for_course(course_code, cursor)
            prereqs_lower = get_prerequisites_for_course(lowercase_code, cursor)
            
            assert prereqs_upper == prereqs_lower
        
        conn.close()

"""
Integration tests for database integrity and security.

Tests:
- Table existence and schema
- Data integrity
- SQL injection prevention
"""

import pytest
import sqlite3

from actions.system.db_utils import get_db_connection
from tests.helpers import create_tracker, get_slot_value

from actions.academic.course_actions import ActionGetCourseDetails


class TestDatabaseSchema:
    """Tests for database schema validation."""

    def test_courses_table_exists(self):
        """DB-001: Courses table exists with expected schema."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "courses table does not exist"

    def test_prerequisites_table_exists(self):
        """DB-002: Prerequisites table exists with expected schema."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prerequisites'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "prerequisites table does not exist"

    def test_courses_table_has_required_columns(self):
        """Courses table has all required columns."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(courses)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        
        required_columns = {"course_code", "course_name", "credit_hours", "description"}
        missing = required_columns - columns
        assert not missing, f"Missing columns in courses table: {missing}"

    def test_prerequisites_table_has_required_columns(self):
        """Prerequisites table has all required columns."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(prerequisites)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        
        required_columns = {"course_code", "prereq_code"}
        missing = required_columns - columns
        assert not missing, f"Missing columns in prerequisites table: {missing}"


class TestDataIntegrity:
    """Tests for data integrity validation."""

    def test_prerequisites_reference_valid_courses(self):
        """DB-003: All prerequisite codes reference valid courses (excluding special values)."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find any prereq_code that doesn't exist in courses
        cursor.execute("""
            SELECT p.prereq_code 
            FROM prerequisites p 
            LEFT JOIN courses c ON p.prereq_code = c.course_code 
            WHERE c.course_code IS NULL
              AND p.prereq_code NOT LIKE '%PERMISSION%'
              AND p.prereq_code NOT LIKE '%APPROVAL%'
        """)
        invalid_refs = cursor.fetchall()
        conn.close()
        
        assert len(invalid_refs) == 0, f"Invalid prerequisite references: {invalid_refs}"

    def test_course_codes_unique(self):
        """DB-004: Course codes are unique (no duplicates)."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT course_code, COUNT(*) as cnt 
            FROM courses 
            GROUP BY course_code 
            HAVING cnt > 1
        """)
        duplicates = cursor.fetchall()
        conn.close()
        
        assert len(duplicates) == 0, f"Duplicate course codes found: {duplicates}"

    def test_all_courses_have_names(self):
        """All courses have non-null names."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT course_code FROM courses WHERE course_name IS NULL")
        null_names = cursor.fetchall()
        conn.close()
        
        assert len(null_names) == 0, f"Courses with null names: {null_names}"


class TestSecuritySqlInjection:
    """Tests for SQL injection prevention."""

    def test_sql_injection_course_code(self, dispatcher, domain):
        """SEC-001: SQL injection attempt is handled safely."""
        # Attempt SQL injection through course_code
        malicious_input = "'; DROP TABLE courses; --"
        tracker = create_tracker(slots={"course_code": malicious_input})
        action = ActionGetCourseDetails()
        
        # Should not raise exception and should return not found
        events = action.run(dispatcher, tracker, domain)
        return_value = get_slot_value(events, "return_value")
        
        assert return_value == "course_not_found"
        
        # Verify table still exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "SQL injection succeeded - table was dropped!"

    def test_sql_injection_union_attack(self, dispatcher, domain):
        """SEC-002: UNION-based SQL injection is prevented."""
        malicious_input = "CCS3101' UNION SELECT * FROM sqlite_master --"
        tracker = create_tracker(slots={"course_code": malicious_input})
        action = ActionGetCourseDetails()
        
        # Should handle gracefully
        events = action.run(dispatcher, tracker, domain)
        return_value = get_slot_value(events, "return_value")
        
        # Should return not found, not expose data
        assert return_value == "course_not_found"

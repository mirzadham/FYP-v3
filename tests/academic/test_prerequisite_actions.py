"""
Tests for prerequisite-related actions.

Tests:
- ActionCheckPrerequisites
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.academic.prerequisite_actions import ActionCheckPrerequisites
from actions.system.db_utils import get_db_connection


class TestActionCheckPrerequisites:
    """Tests for ActionCheckPrerequisites action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckPrerequisites()
        assert action.name() == "check_prerequisites"

    def test_course_with_prerequisites(self, dispatcher, domain):
        """UT-009: Course with prerequisites returns has_prerequisites=True."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT course_code FROM prerequisites LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            course_code = result[0]
            tracker = create_tracker(slots={"course_code": course_code})
            action = ActionCheckPrerequisites()
            
            events = action.run(dispatcher, tracker, domain)
            has_prereqs = get_slot_value(events, "has_prerequisites")
            
            assert has_prereqs is True

    def test_course_without_prerequisites(self, dispatcher, domain):
        """UT-010: Course without prerequisites returns has_prerequisites=False."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.course_code 
            FROM courses c 
            LEFT JOIN prerequisites p ON c.course_code = p.course_code 
            WHERE p.course_code IS NULL 
            LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            course_code = result[0]
            tracker = create_tracker(slots={"course_code": course_code})
            action = ActionCheckPrerequisites()
            
            events = action.run(dispatcher, tracker, domain)
            has_prereqs = get_slot_value(events, "has_prerequisites")
            
            assert has_prereqs is False

    def test_nonexistent_course(self, dispatcher, domain):
        """UT-011: Non-existent course returns course_not_found."""
        tracker = create_tracker(slots={"course_code": "FAKE123"})
        action = ActionCheckPrerequisites()
        
        events = action.run(dispatcher, tracker, domain)
        return_value = get_slot_value(events, "return_value")
        
        assert return_value == "course_not_found"

    def test_null_course_code_slot(self, dispatcher, domain):
        """UT-012: Null course code slot returns course_not_found."""
        tracker = create_tracker(slots={"course_code": None})
        action = ActionCheckPrerequisites()
        
        events = action.run(dispatcher, tracker, domain)
        return_value = get_slot_value(events, "return_value")
        
        assert return_value == "course_not_found"

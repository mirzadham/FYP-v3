"""
Pytest tests for Academic Advisor Chatbot custom actions.
Tests all custom actions defined in actions/actions.py

Run tests with: pytest tests/test_actions.py -v
"""

import pytest
import sqlite3
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.actions import (
    ActionGetCourseDetails,
    ActionCheckPrerequisites,
    ActionOpenAIResponse,
    get_db_connection,
    get_prerequisites_for_course,
    DB_PATH
)
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher


# ============================================================================
# Helper Functions
# ============================================================================

def get_slot_value(events, slot_name):
    """Extract slot value from events list (handles SlotSet objects and dicts)."""
    for e in events:
        # Handle SlotSet objects (duck typing)
        if hasattr(e, 'key') and hasattr(e, 'value'):
            if e.key == slot_name:
                return e.value
        # Handle dict representation - Rasa uses 'name' for slot name
        elif isinstance(e, dict):
            if e.get('name') == slot_name:
                return e.get('value')
            # Also try 'slot' key for compatibility
            elif e.get('slot') == slot_name:
                return e.get('value')
    return None


def get_all_slot_names(events):
    """Extract all slot names from events list."""
    slot_names = set()
    for e in events:
        if hasattr(e, 'key'):
            slot_names.add(e.key)
        elif isinstance(e, dict):
            if 'name' in e:
                slot_names.add(e['name'])
            elif 'slot' in e:
                slot_names.add(e['slot'])
    return slot_names


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def dispatcher():
    """Create a mock dispatcher for testing."""
    return Mock(spec=CollectingDispatcher)


@pytest.fixture
def domain():
    """Create a mock domain for testing."""
    return {}


def create_tracker(slots=None, latest_message=None):
    """Helper to create a mock tracker with specified slots."""
    tracker = Mock(spec=Tracker)
    tracker.get_slot = Mock(side_effect=lambda key: (slots or {}).get(key))
    tracker.latest_message = latest_message or {"text": ""}
    return tracker


# ============================================================================
# Database Helper Tests
# ============================================================================

class TestDatabaseHelpers:
    """Tests for database helper functions."""

    def test_get_db_connection_returns_connection(self):
        """UT-017: get_db_connection() returns valid SQLite connection."""
        conn = get_db_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_get_db_connection_path_exists(self):
        """Verify database file exists at expected path."""
        assert os.path.exists(DB_PATH), f"Database not found at {DB_PATH}"

    def test_get_prerequisites_for_course_with_prereqs(self):
        """UT-018: get_prerequisites_for_course() returns formatted list for course with prereqs."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First find a course with prerequisites
        cursor.execute("""
            SELECT DISTINCT course_code FROM prerequisites LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            course_code = result[0]
            prereqs = get_prerequisites_for_course(course_code, cursor)
            assert prereqs is not None
            assert isinstance(prereqs, str)
            assert "•" in prereqs  # Check formatting
        
        conn.close()

    def test_get_prerequisites_for_course_without_prereqs(self):
        """UT-019: get_prerequisites_for_course() returns None for course without prereqs."""
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

    def test_get_prerequisites_for_invalid_course(self):
        """get_prerequisites_for_course() returns None for non-existent course."""
        conn = get_db_connection()
        cursor = conn.cursor()
        prereqs = get_prerequisites_for_course("INVALID999", cursor)
        assert prereqs is None
        conn.close()


# ============================================================================
# ActionGetCourseDetails Tests
# ============================================================================

class TestActionGetCourseDetails:
    """Tests for ActionGetCourseDetails action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionGetCourseDetails()
        assert action.name() == "get_course_details"

    def test_valid_course_code_uppercase(self, dispatcher, domain):
        """UT-001: Valid course code (uppercase) returns course details."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_code FROM courses LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            course_code = result[0]
            tracker = create_tracker(slots={"course_code": course_code})
            action = ActionGetCourseDetails()
            
            events = action.run(dispatcher, tracker, domain)
            return_value = get_slot_value(events, "return_value")
            
            assert return_value == "course_found"

    def test_valid_course_code_lowercase(self, dispatcher, domain):
        """UT-002: Valid course code (lowercase) normalizes and returns details."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_code FROM courses LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            course_code = result[0].lower()  # Convert to lowercase
            tracker = create_tracker(slots={"course_code": course_code})
            action = ActionGetCourseDetails()
            
            events = action.run(dispatcher, tracker, domain)
            return_value = get_slot_value(events, "return_value")
            
            assert return_value == "course_found"

    def test_invalid_course_code(self, dispatcher, domain):
        """UT-003: Invalid course code returns course_not_found."""
        tracker = create_tracker(slots={"course_code": "INVALID999"})
        action = ActionGetCourseDetails()
        
        events = action.run(dispatcher, tracker, domain)
        return_value = get_slot_value(events, "return_value")
        
        assert return_value == "course_not_found"

    def test_empty_course_code(self, dispatcher, domain):
        """UT-004: Empty course code returns course_not_found."""
        tracker = create_tracker(slots={"course_code": ""})
        action = ActionGetCourseDetails()
        
        events = action.run(dispatcher, tracker, domain)
        return_value = get_slot_value(events, "return_value")
        
        assert return_value == "course_not_found"

    def test_none_course_code(self, dispatcher, domain):
        """UT-005: None course code returns course_not_found."""
        tracker = create_tracker(slots={"course_code": None})
        action = ActionGetCourseDetails()
        
        events = action.run(dispatcher, tracker, domain)
        return_value = get_slot_value(events, "return_value")
        
        assert return_value == "course_not_found"

    def test_returns_all_required_slots(self, dispatcher, domain):
        """UT-006: Valid course returns all required slot values."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_code FROM courses LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            course_code = result[0]
            tracker = create_tracker(slots={"course_code": course_code})
            action = ActionGetCourseDetails()
            
            events = action.run(dispatcher, tracker, domain)
            slot_names = get_all_slot_names(events)
            
            expected_slots = {"course_code", "course_name", "credits", "synopsis", "prereq_list", "return_value"}
            assert expected_slots.issubset(slot_names)


# ============================================================================
# ActionCheckPrerequisites Tests
# ============================================================================

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


# ============================================================================
# ActionOpenAIResponse Tests
# ============================================================================

class TestActionOpenAIResponse:
    """Tests for ActionOpenAIResponse action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionOpenAIResponse()
        assert action.name() == "action_openai_response"

    def test_empty_user_message(self, dispatcher, domain):
        """UT-014: Empty user message returns fallback message."""
        tracker = create_tracker(latest_message={"text": ""})
        action = ActionOpenAIResponse()
        
        events = action.run(dispatcher, tracker, domain)
        
        # Verify dispatcher was called with fallback message
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        assert "rephrase" in call_args[1]["text"].lower() or "not sure" in call_args[1]["text"].lower()

    @patch('actions.actions.OpenAI')
    def test_valid_user_message(self, mock_openai, dispatcher, domain):
        """UT-013: Valid user message calls OpenAI and returns response."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response from OpenAI"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        tracker = create_tracker(latest_message={"text": "What courses are available?"})
        action = ActionOpenAIResponse()
        
        events = action.run(dispatcher, tracker, domain)
        
        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()
        # Verify dispatcher got the response
        dispatcher.utter_message.assert_called_with(text="Test response from OpenAI")

    @patch('actions.actions.OpenAI')
    def test_openai_api_error(self, mock_openai, dispatcher, domain):
        """UT-015: OpenAI API error returns error message with contact info."""
        # Mock OpenAI to raise an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        tracker = create_tracker(latest_message={"text": "Some question"})
        action = ActionOpenAIResponse()
        
        events = action.run(dispatcher, tracker, domain)
        
        # Verify error message was sent
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        assert "trouble" in call_args[1]["text"].lower() or "error" in call_args[1]["text"].lower()

    def test_context_retrieval(self, dispatcher, domain):
        """UT-016: Context retrieval returns relevant context from database."""
        action = ActionOpenAIResponse()
        
        # Test internal method directly
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course_name FROM courses LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Use a keyword from actual course name
            keyword = result[0].split()[0] if result[0] else "programming"
            context = action._get_relevant_context(keyword)
            assert isinstance(context, str)


# ============================================================================
# Database Integrity Tests
# ============================================================================

class TestDatabaseIntegrity:
    """Tests for database data integrity."""

    def test_courses_table_exists(self):
        """DB-001: Courses table exists with expected schema."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None

    def test_prerequisites_table_exists(self):
        """DB-002: Prerequisites table exists with expected schema."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prerequisites'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None

    def test_prerequisites_reference_valid_courses(self):
        """DB-003: All prerequisite codes reference valid courses (excluding special values)."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find any prereq_code that doesn't exist in courses
        # Note: Some prerequisites like DEPT_PERMISSION are not course codes
        # but represent special requirements (e.g., department permission)
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


# ============================================================================
# Security Tests
# ============================================================================

class TestSecurity:
    """Security-related tests."""

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


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests for course-related actions.

Tests:
- ActionGetCourseDetails
- ActionValidateCourseCodeFormat
- ActionResetCourseCode
"""

import pytest
from tests.helpers import create_tracker, get_slot_value, get_all_slot_names

from actions.academic.course_actions import ActionGetCourseDetails
from actions.academic.prerequisite_actions import (
    ActionValidateCourseCodeFormat,
    ActionResetCourseCode,
)


class TestActionGetCourseDetails:
    """Tests for ActionGetCourseDetails action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionGetCourseDetails()
        assert action.name() == "get_course_details"

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


class TestActionValidateCourseCodeFormat:
    """Tests for ActionValidateCourseCodeFormat action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionValidateCourseCodeFormat()
        assert action.name() == "validate_course_code_format"

    def test_valid_format(self, dispatcher, domain):
        """UT-013: Valid course code format passes validation."""
        tracker = create_tracker(slots={"course_code": "CCS3101"})
        action = ActionValidateCourseCodeFormat()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "course_code_valid")
        
        assert is_valid is True

    def test_invalid_format_too_short(self, dispatcher, domain):
        """UT-014: Invalid course code format fails validation."""
        tracker = create_tracker(slots={"course_code": "ABC"})
        action = ActionValidateCourseCodeFormat()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "course_code_valid")
        
        assert is_valid is False

    def test_none_course_code(self, dispatcher, domain):
        """None course code fails validation."""
        tracker = create_tracker(slots={"course_code": None})
        action = ActionValidateCourseCodeFormat()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "course_code_valid")
        
        assert is_valid is False


class TestActionResetCourseCode:
    """Tests for ActionResetCourseCode action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetCourseCode()
        assert action.name() == "reset_course_code"

    def test_reset_slots(self, dispatcher, domain):
        """UT-016: Reset clears course_code and course_code_valid slots."""
        tracker = create_tracker(slots={"course_code": "CCS3101", "course_code_valid": True})
        action = ActionResetCourseCode()
        
        events = action.run(dispatcher, tracker, domain)
        
        course_code = get_slot_value(events, "course_code")
        course_code_valid = get_slot_value(events, "course_code_valid")
        
        assert course_code is None
        assert course_code_valid is None

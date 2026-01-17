"""
Tests for prerequisite-related actions.

Tests:
- ActionCheckPrerequisites
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.academic.prerequisite_actions import ActionCheckPrerequisites


class TestActionCheckPrerequisites:
    """Tests for ActionCheckPrerequisites action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckPrerequisites()
        assert action.name() == "check_prerequisites"

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

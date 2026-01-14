"""
Tests for drop course-related actions.

Tests:
- ActionCheckDropAssessmentChoice
- ActionValidateWeek
- ActionResetWeek
- ActionAssessDropConsequences
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.academic.drop_course_actions import (
    ActionCheckDropAssessmentChoice,
    ActionValidateWeek,
    ActionResetWeek,
    ActionAssessDropConsequences,
)


class TestActionCheckDropAssessmentChoice:
    """Tests for ActionCheckDropAssessmentChoice action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckDropAssessmentChoice()
        assert action.name() == "action_check_drop_assessment_choice"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events (slot set by LLM)."""
        tracker = create_tracker(slots={"wants_drop_assessment": True})
        action = ActionCheckDropAssessmentChoice()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionValidateWeek:
    """Tests for ActionValidateWeek action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionValidateWeek()
        assert action.name() == "action_validate_week"

    def test_valid_week_in_range(self, dispatcher, domain):
        """UT-038: Valid week (1-14) passes validation."""
        tracker = create_tracker(slots={"current_week": 8})
        action = ActionValidateWeek()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "week_valid")
        
        assert is_valid is True

    def test_invalid_week_too_high(self, dispatcher, domain):
        """UT-039: Invalid week (>14) fails validation."""
        tracker = create_tracker(slots={"current_week": 20})
        action = ActionValidateWeek()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "week_valid")
        
        assert is_valid is False

    def test_invalid_week_zero(self, dispatcher, domain):
        """UT-040: Zero week fails validation."""
        tracker = create_tracker(slots={"current_week": 0})
        action = ActionValidateWeek()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "week_valid")
        
        assert is_valid is False

    def test_boundary_week_1(self, dispatcher, domain):
        """Boundary: Week 1 is valid."""
        tracker = create_tracker(slots={"current_week": 1})
        action = ActionValidateWeek()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "week_valid")
        
        assert is_valid is True

    def test_boundary_week_14(self, dispatcher, domain):
        """Boundary: Week 14 is valid."""
        tracker = create_tracker(slots={"current_week": 14})
        action = ActionValidateWeek()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "week_valid")
        
        assert is_valid is True


class TestActionResetWeek:
    """Tests for ActionResetWeek action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetWeek()
        assert action.name() == "action_reset_week"

    def test_reset_clears_slots(self, dispatcher, domain):
        """Reset clears current_week and week_valid slots."""
        tracker = create_tracker(slots={"current_week": 8, "week_valid": True})
        action = ActionResetWeek()
        
        events = action.run(dispatcher, tracker, domain)
        
        week = get_slot_value(events, "current_week")
        valid = get_slot_value(events, "week_valid")
        
        assert week is None
        assert valid is None


class TestActionAssessDropConsequences:
    """Tests for ActionAssessDropConsequences action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessDropConsequences()
        assert action.name() == "action_assess_drop_consequences"

    def test_free_drop_week_2(self, dispatcher, domain):
        """UT-041: Week 1-2 is free (no penalty)."""
        tracker = create_tracker(slots={"current_week": 2})
        action = ActionAssessDropConsequences()
        
        events = action.run(dispatcher, tracker, domain)
        phase = get_slot_value(events, "drop_phase")
        
        assert phase == "free"

    def test_late_drop_week_5(self, dispatcher, domain):
        """UT-042: Week 3-7 is late (W grade, penalty)."""
        tracker = create_tracker(slots={"current_week": 5})
        action = ActionAssessDropConsequences()
        
        events = action.run(dispatcher, tracker, domain)
        phase = get_slot_value(events, "drop_phase")
        
        assert phase == "late"

    def test_closed_drop_week_14(self, dispatcher, domain):
        """UT-043: After week 12 is closed (cannot drop)."""
        tracker = create_tracker(slots={"current_week": 14})
        action = ActionAssessDropConsequences()
        
        events = action.run(dispatcher, tracker, domain)
        phase = get_slot_value(events, "drop_phase")
        
        assert phase == "closed"

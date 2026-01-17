"""
Tests for deferment-related actions.

Tests:
- ActionAssessDefermentTiming
- ActionProvideTimingWarning
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.policies.deferment_actions import (
    ActionAssessDefermentTiming,
    ActionProvideTimingWarning,
)


class TestActionAssessDefermentTiming:
    """Tests for ActionAssessDefermentTiming action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessDefermentTiming()
        assert action.name() == "action_assess_deferment_timing"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events (pass-through action)."""
        tracker = create_tracker(slots={"deferment_reason": "medical"})
        action = ActionAssessDefermentTiming()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionProvideTimingWarning:
    """Tests for ActionProvideTimingWarning action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionProvideTimingWarning()
        assert action.name() == "action_provide_timing_warning"

    def test_early_week_not_late(self, dispatcher, domain):
        """Week 1-4 should NOT be considered late."""
        tracker = create_tracker(slots={"current_semester_week": 2})
        action = ActionProvideTimingWarning()
        
        events = action.run(dispatcher, tracker, domain)
        is_late = get_slot_value(events, "is_late_deferment")
        
        assert is_late is False

    def test_week_4_boundary_not_late(self, dispatcher, domain):
        """Boundary: Week 4 is still NOT late."""
        tracker = create_tracker(slots={"current_semester_week": 4})
        action = ActionProvideTimingWarning()
        
        events = action.run(dispatcher, tracker, domain)
        is_late = get_slot_value(events, "is_late_deferment")
        
        assert is_late is False

    def test_week_5_is_late(self, dispatcher, domain):
        """Week 5+ should be considered late."""
        tracker = create_tracker(slots={"current_semester_week": 5})
        action = ActionProvideTimingWarning()
        
        events = action.run(dispatcher, tracker, domain)
        is_late = get_slot_value(events, "is_late_deferment")
        
        assert is_late is True

    def test_very_late_week(self, dispatcher, domain):
        """Week 10+ is definitely late."""
        tracker = create_tracker(slots={"current_semester_week": 10})
        action = ActionProvideTimingWarning()
        
        events = action.run(dispatcher, tracker, domain)
        is_late = get_slot_value(events, "is_late_deferment")
        
        assert is_late is True

    def test_none_week_defaults_to_not_late(self, dispatcher, domain):
        """None week should default to week 1 (not late)."""
        tracker = create_tracker(slots={"current_semester_week": None})
        action = ActionProvideTimingWarning()
        
        events = action.run(dispatcher, tracker, domain)
        is_late = get_slot_value(events, "is_late_deferment")
        
        assert is_late is False

    def test_string_week_converts(self, dispatcher, domain):
        """String week value should be converted to int."""
        tracker = create_tracker(slots={"current_semester_week": "6"})
        action = ActionProvideTimingWarning()
        
        events = action.run(dispatcher, tracker, domain)
        is_late = get_slot_value(events, "is_late_deferment")
        
        assert is_late is True

    def test_invalid_string_defaults_to_not_late(self, dispatcher, domain):
        """Invalid string defaults to week 1 (not late)."""
        tracker = create_tracker(slots={"current_semester_week": "invalid"})
        action = ActionProvideTimingWarning()
        
        events = action.run(dispatcher, tracker, domain)
        is_late = get_slot_value(events, "is_late_deferment")
        
        assert is_late is False

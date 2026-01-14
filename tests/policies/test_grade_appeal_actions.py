"""
Tests for grade appeal-related actions.

Tests:
- ActionCheckAppealChoice
- ActionValidateDays
- ActionResetDays
- ActionCheckAppealDeadline
- ActionAssessAppealReadiness
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.policies.grade_appeal_actions import (
    ActionCheckAppealChoice,
    ActionValidateDays,
    ActionResetDays,
    ActionCheckAppealDeadline,
    ActionAssessAppealReadiness,
)


class TestActionCheckAppealChoice:
    """Tests for ActionCheckAppealChoice action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckAppealChoice()
        assert action.name() == "action_check_appeal_choice"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events (slot set by LLM)."""
        tracker = create_tracker(slots={"wants_appeal_assessment": True})
        action = ActionCheckAppealChoice()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionValidateDays:
    """Tests for ActionValidateDays action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionValidateDays()
        assert action.name() == "action_validate_days"

    def test_valid_days(self, dispatcher, domain):
        """UT-060: Valid days passes validation."""
        tracker = create_tracker(slots={"days_since_results": 5})
        action = ActionValidateDays()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "days_valid")
        
        assert is_valid is True

    def test_negative_days_invalid(self, dispatcher, domain):
        """UT-061: Negative days fails validation."""
        tracker = create_tracker(slots={"days_since_results": -1})
        action = ActionValidateDays()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "days_valid")
        
        assert is_valid is False

    def test_zero_days_valid(self, dispatcher, domain):
        """Zero days is valid (same day)."""
        tracker = create_tracker(slots={"days_since_results": 0})
        action = ActionValidateDays()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "days_valid")
        
        assert is_valid is True

    def test_none_days_invalid(self, dispatcher, domain):
        """None days fails validation."""
        tracker = create_tracker(slots={"days_since_results": None})
        action = ActionValidateDays()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "days_valid")
        
        assert is_valid is False


class TestActionResetDays:
    """Tests for ActionResetDays action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetDays()
        assert action.name() == "action_reset_days"

    def test_reset_clears_slots(self, dispatcher, domain):
        """Reset clears days_since_results and days_valid slots."""
        tracker = create_tracker(slots={"days_since_results": 5, "days_valid": True})
        action = ActionResetDays()
        
        events = action.run(dispatcher, tracker, domain)
        
        days = get_slot_value(events, "days_since_results")
        valid = get_slot_value(events, "days_valid")
        
        assert days is None
        assert valid is None


class TestActionCheckAppealDeadline:
    """Tests for ActionCheckAppealDeadline action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckAppealDeadline()
        assert action.name() == "action_check_appeal_deadline"

    def test_within_deadline(self, dispatcher, domain):
        """UT-062: Within deadline (≤14 days)."""
        tracker = create_tracker(slots={"days_since_results": 10})
        action = ActionCheckAppealDeadline()
        
        events = action.run(dispatcher, tracker, domain)
        within = get_slot_value(events, "within_deadline")
        
        assert within is True

    def test_past_deadline(self, dispatcher, domain):
        """UT-063: Past deadline (>14 days)."""
        tracker = create_tracker(slots={"days_since_results": 20})
        action = ActionCheckAppealDeadline()
        
        events = action.run(dispatcher, tracker, domain)
        within = get_slot_value(events, "within_deadline")
        
        assert within is False

    def test_boundary_exactly_14_days(self, dispatcher, domain):
        """Boundary: Exactly 14 days is within deadline."""
        tracker = create_tracker(slots={"days_since_results": 14})
        action = ActionCheckAppealDeadline()
        
        events = action.run(dispatcher, tracker, domain)
        within = get_slot_value(events, "within_deadline")
        
        assert within is True


class TestActionAssessAppealReadiness:
    """Tests for ActionAssessAppealReadiness action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessAppealReadiness()
        assert action.name() == "action_assess_appeal_readiness"

    def test_should_review_when_not_reviewed(self, dispatcher, domain):
        """Recommends review when hasn't reviewed script yet."""
        tracker = create_tracker(slots={
            "has_reviewed_script": False
        })
        action = ActionAssessAppealReadiness()
        
        events = action.run(dispatcher, tracker, domain)
        should_review = get_slot_value(events, "should_review_first")
        
        assert should_review is True

    def test_no_review_when_already_reviewed(self, dispatcher, domain):
        """Doesn't recommend review when already reviewed script."""
        tracker = create_tracker(slots={
            "has_reviewed_script": True
        })
        action = ActionAssessAppealReadiness()
        
        events = action.run(dispatcher, tracker, domain)
        should_review = get_slot_value(events, "should_review_first")
        
        assert should_review is False

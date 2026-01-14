"""
Tests for industrial training (LI) related actions.

Tests:
- ActionCheckLiAssessmentChoice
- ActionValidateYear
- ActionResetYear
- ActionAssessLiEligibility
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.policies.industrial_training_actions import (
    ActionCheckLiAssessmentChoice,
    ActionValidateYear,
    ActionResetYear,
    ActionAssessLiEligibility,
)


class TestActionCheckLiAssessmentChoice:
    """Tests for ActionCheckLiAssessmentChoice action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckLiAssessmentChoice()
        assert action.name() == "action_check_li_assessment_choice"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events (slot set by LLM)."""
        tracker = create_tracker(slots={"wants_li_assessment": True})
        action = ActionCheckLiAssessmentChoice()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionValidateYear:
    """Tests for ActionValidateYear action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionValidateYear()
        assert action.name() == "action_validate_year"

    def test_valid_year(self, dispatcher, domain):
        """UT-056: Valid year (1-4) passes validation."""
        tracker = create_tracker(slots={"current_year": 3})
        action = ActionValidateYear()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "year_valid")
        
        assert is_valid is True

    def test_invalid_year_zero(self, dispatcher, domain):
        """UT-057: Invalid year (0) fails validation."""
        tracker = create_tracker(slots={"current_year": 0})
        action = ActionValidateYear()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "year_valid")
        
        assert is_valid is False

    def test_invalid_year_too_high(self, dispatcher, domain):
        """Invalid year (>4) fails validation."""
        tracker = create_tracker(slots={"current_year": 6})
        action = ActionValidateYear()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "year_valid")
        
        assert is_valid is False

    def test_none_year_invalid(self, dispatcher, domain):
        """None year fails validation."""
        tracker = create_tracker(slots={"current_year": None})
        action = ActionValidateYear()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "year_valid")
        
        assert is_valid is False


class TestActionResetYear:
    """Tests for ActionResetYear action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetYear()
        assert action.name() == "action_reset_year"

    def test_reset_clears_slots(self, dispatcher, domain):
        """Reset clears current_year and year_valid slots."""
        tracker = create_tracker(slots={"current_year": 3, "year_valid": True})
        action = ActionResetYear()
        
        events = action.run(dispatcher, tracker, domain)
        
        year = get_slot_value(events, "current_year")
        valid = get_slot_value(events, "year_valid")
        
        assert year is None
        assert valid is None


class TestActionAssessLiEligibility:
    """Tests for ActionAssessLiEligibility action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessLiEligibility()
        assert action.name() == "action_assess_li_eligibility"

    def test_eligible_year_3(self, dispatcher, domain):
        """UT-058: Eligible (Year 3+ with sufficient credits)."""
        tracker = create_tracker(slots={
            "current_year": 3,
            "credits_completed": 80,
            "is_on_probation": False
        })
        action = ActionAssessLiEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "li_eligible")
        
        assert eligible is True

    def test_not_eligible_year_2(self, dispatcher, domain):
        """UT-059: Not eligible (Year 1-2)."""
        tracker = create_tracker(slots={
            "current_year": 2,
            "credits_completed": 80,
            "is_on_probation": False
        })
        action = ActionAssessLiEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "li_eligible")
        
        assert eligible is False

    def test_eligible_year_4(self, dispatcher, domain):
        """Year 4 is also eligible with sufficient credits."""
        tracker = create_tracker(slots={
            "current_year": 4,
            "credits_completed": 90,
            "is_on_probation": False
        })
        action = ActionAssessLiEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "li_eligible")
        
        assert eligible is True

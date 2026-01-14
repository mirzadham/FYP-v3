"""
Tests for convocation-related actions.

Tests:
- ActionCheckEligibilityChoice
- ActionValidateMuet
- ActionResetMuet
- ActionAssessConvocationEligibility
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.academic.convocation_actions import (
    ActionCheckEligibilityChoice,
    ActionValidateMuet,
    ActionResetMuet,
    ActionAssessConvocationEligibility,
)


class TestActionCheckEligibilityChoice:
    """Tests for ActionCheckEligibilityChoice action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckEligibilityChoice()
        assert action.name() == "action_check_eligibility_choice"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events (slot set by LLM)."""
        tracker = create_tracker(slots={"wants_eligibility_check": True})
        action = ActionCheckEligibilityChoice()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionValidateMuet:
    """Tests for ActionValidateMuet action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionValidateMuet()
        assert action.name() == "action_validate_muet"

    def test_valid_band_4(self, dispatcher, domain):
        """UT-032: Valid band (4) passes validation."""
        tracker = create_tracker(slots={"muet_band": 4})
        action = ActionValidateMuet()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "muet_valid")
        
        assert is_valid is True

    def test_valid_band_string(self, dispatcher, domain):
        """UT-035: String number passes validation."""
        tracker = create_tracker(slots={"muet_band": "5"})
        action = ActionValidateMuet()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "muet_valid")
        
        assert is_valid is True

    def test_invalid_band_too_high(self, dispatcher, domain):
        """UT-033: Invalid band (>6) fails validation."""
        tracker = create_tracker(slots={"muet_band": 8})
        action = ActionValidateMuet()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "muet_valid")
        
        assert is_valid is False

    def test_invalid_band_too_low(self, dispatcher, domain):
        """UT-034: Invalid band (<0) fails validation."""
        tracker = create_tracker(slots={"muet_band": -1})
        action = ActionValidateMuet()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "muet_valid")
        
        assert is_valid is False

    def test_none_band_invalid(self, dispatcher, domain):
        """None band fails validation."""
        tracker = create_tracker(slots={"muet_band": None})
        action = ActionValidateMuet()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "muet_valid")
        
        assert is_valid is False


class TestActionResetMuet:
    """Tests for ActionResetMuet action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetMuet()
        assert action.name() == "action_reset_muet"

    def test_reset_clears_slots(self, dispatcher, domain):
        """Reset clears muet_band and muet_valid slots."""
        tracker = create_tracker(slots={"muet_band": 4, "muet_valid": True})
        action = ActionResetMuet()
        
        events = action.run(dispatcher, tracker, domain)
        
        band = get_slot_value(events, "muet_band")
        valid = get_slot_value(events, "muet_valid")
        
        assert band is None
        assert valid is None


class TestActionAssessConvocationEligibility:
    """Tests for ActionAssessConvocationEligibility action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessConvocationEligibility()
        assert action.name() == "action_assess_convocation_eligibility"

    def test_eligible_muet_band_4(self, dispatcher, domain):
        """UT-036: Eligible with all requirements met."""
        tracker = create_tracker(slots={
            "muet_band": 4,
            "credits_completed": 120,
            "current_cgpa": 2.5,
            "has_outstanding_fees": False
        })
        action = ActionAssessConvocationEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "eligibility_status")
        
        assert status == "eligible"

    def test_not_eligible_muet_band_2(self, dispatcher, domain):
        """UT-037: Not eligible (MUET <3)."""
        tracker = create_tracker(slots={
            "muet_band": 2,
            "credits_completed": 120,
            "current_cgpa": 2.5,
            "has_outstanding_fees": False
        })
        action = ActionAssessConvocationEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "eligibility_status")
        
        # partial because only MUET fails
        assert status == "partial"

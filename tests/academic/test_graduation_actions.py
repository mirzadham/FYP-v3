"""
Tests for graduation-related actions.

Tests:
- ActionCheckGraduationAssessmentChoice
- ActionValidateCredits
- ActionResetCredits
- ActionAssessGraduationStatus
- ActionResetGraduationSlots
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.academic.graduation_actions import (
    ActionCheckGraduationAssessmentChoice,
    ActionValidateCredits,
    ActionResetCredits,
    ActionAssessGraduationStatus,
    ActionResetGraduationSlots,
)


class TestActionCheckGraduationAssessmentChoice:
    """Tests for ActionCheckGraduationAssessmentChoice action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckGraduationAssessmentChoice()
        assert action.name() == "action_check_graduation_assessment_choice"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events (slot set by LLM)."""
        tracker = create_tracker(slots={"wants_graduation_assessment": True})
        action = ActionCheckGraduationAssessmentChoice()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionValidateCredits:
    """Tests for ActionValidateCredits action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionValidateCredits()
        assert action.name() == "action_validate_credits"

    def test_valid_credits_integer(self, dispatcher, domain):
        """UT-017: Valid credits (int) passes validation."""
        tracker = create_tracker(slots={"credits_completed": 90})
        action = ActionValidateCredits()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "credits_valid")
        
        assert is_valid is True

    def test_valid_credits_string(self, dispatcher, domain):
        """UT-018: Valid credits (string) passes validation."""
        tracker = create_tracker(slots={"credits_completed": "120"})
        action = ActionValidateCredits()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "credits_valid")
        
        assert is_valid is True

    def test_valid_credits_float_rounds(self, dispatcher, domain):
        """UT-019: Float credits rounds to integer."""
        tracker = create_tracker(slots={"credits_completed": 95.5})
        action = ActionValidateCredits()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "credits_valid")
        credits = get_slot_value(events, "credits_completed")
        
        assert is_valid is True
        assert credits == 96  # Rounded

    def test_negative_credits_invalid(self, dispatcher, domain):
        """UT-020: Negative credits fails validation."""
        tracker = create_tracker(slots={"credits_completed": -10})
        action = ActionValidateCredits()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "credits_valid")
        
        assert is_valid is False

    def test_exceeds_max_invalid(self, dispatcher, domain):
        """UT-021: Credits >150 fails validation."""
        tracker = create_tracker(slots={"credits_completed": 200})
        action = ActionValidateCredits()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "credits_valid")
        
        assert is_valid is False

    def test_none_credits_invalid(self, dispatcher, domain):
        """UT-022: None credits fails validation."""
        tracker = create_tracker(slots={"credits_completed": None})
        action = ActionValidateCredits()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "credits_valid")
        
        assert is_valid is False

    def test_invalid_string_credits(self, dispatcher, domain):
        """UT-023: Non-numeric string fails validation."""
        tracker = create_tracker(slots={"credits_completed": "abc"})
        action = ActionValidateCredits()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "credits_valid")
        
        assert is_valid is False

    def test_zero_credits_valid(self, dispatcher, domain):
        """UT-024: Zero credits is valid."""
        tracker = create_tracker(slots={"credits_completed": 0})
        action = ActionValidateCredits()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "credits_valid")
        
        assert is_valid is True


class TestActionResetCredits:
    """Tests for ActionResetCredits action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetCredits()
        assert action.name() == "action_reset_credits"

    def test_reset_clears_slots(self, dispatcher, domain):
        """Reset clears credits_completed and credits_valid slots."""
        tracker = create_tracker(slots={"credits_completed": 90, "credits_valid": True})
        action = ActionResetCredits()
        
        events = action.run(dispatcher, tracker, domain)
        
        credits = get_slot_value(events, "credits_completed")
        valid = get_slot_value(events, "credits_valid")
        
        assert credits is None
        assert valid is None


class TestActionAssessGraduationStatus:
    """Tests for ActionAssessGraduationStatus action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessGraduationStatus()
        assert action.name() == "action_assess_graduation_status"

    def test_eligible_status(self, dispatcher, domain):
        """UT-025: Eligible (≥120 credits, ≥2.0 CGPA)."""
        tracker = create_tracker(slots={
            "credits_completed": 120,
            "current_cgpa": 3.0,
            "program_type": "bachelor"
        })
        action = ActionAssessGraduationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "graduation_status")
        
        assert status == "eligible"

    def test_close_status(self, dispatcher, domain):
        """UT-026: Close (within 20 credits)."""
        tracker = create_tracker(slots={
            "credits_completed": 105,
            "current_cgpa": 2.5,
            "program_type": "bachelor"
        })
        action = ActionAssessGraduationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "graduation_status")
        
        assert status == "close"

    def test_in_progress_status(self, dispatcher, domain):
        """UT-027: In progress (40-100 credits)."""
        tracker = create_tracker(slots={
            "credits_completed": 60,
            "current_cgpa": 2.5,
            "program_type": "bachelor"
        })
        action = ActionAssessGraduationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "graduation_status")
        
        assert status == "in_progress"

    def test_early_stage_status(self, dispatcher, domain):
        """UT-028: Early stage (<40 credits)."""
        tracker = create_tracker(slots={
            "credits_completed": 20,
            "current_cgpa": 3.0,
            "program_type": "bachelor"
        })
        action = ActionAssessGraduationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "graduation_status")
        
        assert status == "early_stage"

    def test_diploma_student_eligible(self, dispatcher, domain):
        """UT-029: Diploma student eligible at 90 credits."""
        tracker = create_tracker(slots={
            "credits_completed": 90,
            "current_cgpa": 2.5,
            "program_type": "diploma"
        })
        action = ActionAssessGraduationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "graduation_status")
        
        assert status == "eligible"

    def test_calculates_remaining_credits(self, dispatcher, domain):
        """Calculates remaining credits correctly."""
        tracker = create_tracker(slots={
            "credits_completed": 80,
            "current_cgpa": 2.5,
            "program_type": "bachelor"
        })
        action = ActionAssessGraduationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        remaining = get_slot_value(events, "credits_remaining")
        
        assert remaining == 40  # 120 - 80


class TestActionResetGraduationSlots:
    """Tests for ActionResetGraduationSlots action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetGraduationSlots()
        assert action.name() == "action_reset_graduation_slots"

    def test_resets_all_graduation_slots(self, dispatcher, domain):
        """Resets all graduation-related slots."""
        tracker = create_tracker(slots={
            "credits_completed": 90,
            "graduation_status": "in_progress"
        })
        action = ActionResetGraduationSlots()
        
        events = action.run(dispatcher, tracker, domain)
        
        credits = get_slot_value(events, "credits_completed")
        status = get_slot_value(events, "graduation_status")
        
        assert credits is None
        assert status is None

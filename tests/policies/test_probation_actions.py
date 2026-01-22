"""
Tests for probation-related actions.

Tests:
- ActionCheckAssessmentChoice
- ActionValidateCgpa
- ActionResetCgpa
- ActionAssessProbationStatus
- ActionDetermineProbationLevel
- ActionResetForAssessment
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.helpers import create_tracker, get_slot_value

from actions.policies.probation_actions import (
    ActionCheckAssessmentChoice,
    ActionValidateCgpa,
    ActionResetCgpa,
    ActionAssessProbationStatus,
    ActionDetermineProbationLevel,
    ActionResetForAssessment,
)


class TestActionCheckAssessmentChoice:
    """Tests for ActionCheckAssessmentChoice action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckAssessmentChoice()
        assert action.name() == "action_check_assessment_choice"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events (slot set by LLM)."""
        tracker = create_tracker(slots={"wants_probation_assessment": True})
        action = ActionCheckAssessmentChoice()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionValidateCgpa:
    """Tests for ActionValidateCgpa action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionValidateCgpa()
        assert action.name() == "action_validate_cgpa"

    def test_valid_cgpa(self, dispatcher, domain):
        """UT-044: Valid CGPA (0-4) passes validation."""
        tracker = create_tracker(slots={"current_cgpa": 2.5})
        action = ActionValidateCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "cgpa_valid")
        
        assert is_valid is True

    def test_valid_cgpa_with_comma(self, dispatcher, domain):
        """UT-045: CGPA with comma normalizes and passes."""
        tracker = create_tracker(slots={"current_cgpa": "2,5"})
        action = ActionValidateCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "cgpa_valid")
        cgpa = get_slot_value(events, "current_cgpa")
        
        assert is_valid is True
        assert cgpa == 2.5

    def test_cgpa_above_max_invalid(self, dispatcher, domain):
        """UT-046: CGPA >4.0 fails validation."""
        tracker = create_tracker(slots={"current_cgpa": 4.5})
        action = ActionValidateCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "cgpa_valid")
        
        assert is_valid is False

    def test_negative_cgpa_invalid(self, dispatcher, domain):
        """UT-047: Negative CGPA fails validation."""
        tracker = create_tracker(slots={"current_cgpa": -1.0})
        action = ActionValidateCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "cgpa_valid")
        
        assert is_valid is False

    def test_non_numeric_cgpa_invalid(self, dispatcher, domain):
        """UT-048: Non-numeric CGPA fails validation."""
        tracker = create_tracker(slots={"current_cgpa": "excellent"})
        action = ActionValidateCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "cgpa_valid")
        
        assert is_valid is False

    def test_none_cgpa_invalid(self, dispatcher, domain):
        """None CGPA fails validation."""
        tracker = create_tracker(slots={"current_cgpa": None})
        action = ActionValidateCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "cgpa_valid")
        
        assert is_valid is False

    def test_boundary_cgpa_4_0(self, dispatcher, domain):
        """Boundary: CGPA 4.0 is valid."""
        tracker = create_tracker(slots={"current_cgpa": 4.0})
        action = ActionValidateCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "cgpa_valid")
        
        assert is_valid is True

    def test_boundary_cgpa_0_0(self, dispatcher, domain):
        """Boundary: CGPA 0.0 is valid."""
        tracker = create_tracker(slots={"current_cgpa": 0.0})
        action = ActionValidateCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        is_valid = get_slot_value(events, "cgpa_valid")
        
        assert is_valid is True


class TestActionResetCgpa:
    """Tests for ActionResetCgpa action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetCgpa()
        assert action.name() == "action_reset_cgpa"

    def test_reset_clears_slots(self, dispatcher, domain):
        """Reset clears current_cgpa and cgpa_valid slots."""
        tracker = create_tracker(slots={"current_cgpa": 2.5, "cgpa_valid": True})
        action = ActionResetCgpa()
        
        events = action.run(dispatcher, tracker, domain)
        
        cgpa = get_slot_value(events, "current_cgpa")
        valid = get_slot_value(events, "cgpa_valid")
        
        assert cgpa is None
        assert valid is None


class TestActionAssessProbationStatus:
    """Tests for ActionAssessProbationStatus action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessProbationStatus()
        assert action.name() == "action_assess_probation_status"

    @patch('actions.system.handbook_utils.HandbookStore')
    def test_probation_status_and_context(self, mock_store_cls, dispatcher, domain):
        """UT-049/051: Verify status calculation AND context retrieval."""
        # Mock the store to return a probation rule
        mock_store = MagicMock()
        mock_store.get_all_rules.return_value = {
            "p1": {
                "section_title": "Academic Probation Policy",
                "content_english": "A student with CGPA below 2.00 shall be placed on probation."
            }
        }
        mock_store_cls.return_value = mock_store
        
        # Test Case 1: Probation (1.65)
        tracker = create_tracker(slots={"current_cgpa": 1.65})
        action = ActionAssessProbationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "probation_status")
        context = get_slot_value(events, "probation_context")
        
        assert status == "probation"
        assert "A student with CGPA below 2.00" in context

    @patch('actions.system.handbook_utils.HandbookStore')
    def test_not_on_probation(self, mock_store_cls, dispatcher, domain):
        """UT-049: Not on probation (CGPA >= 2.0)."""
        mock_store_cls.return_value.get_all_rules.return_value = {}
        
        tracker = create_tracker(slots={"current_cgpa": 2.5})
        action = ActionAssessProbationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "probation_status")
        
        assert status == "not_on_probation"

    @patch('actions.system.handbook_utils.HandbookStore')
    def test_warning_status(self, mock_store_cls, dispatcher, domain):
        """UT-050: Warning (CGPA 1.80-1.99)."""
        mock_store_cls.return_value.get_all_rules.return_value = {}
        
        tracker = create_tracker(slots={"current_cgpa": 1.85})
        action = ActionAssessProbationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "probation_status")
        
        assert status == "warning"

    @patch('actions.system.handbook_utils.HandbookStore')
    def test_critical_status(self, mock_store_cls, dispatcher, domain):
        """UT-052: Critical (CGPA <1.50)."""
        mock_store_cls.return_value.get_all_rules.return_value = {}
        
        tracker = create_tracker(slots={"current_cgpa": 1.2})
        action = ActionAssessProbationStatus()
        
        events = action.run(dispatcher, tracker, domain)
        status = get_slot_value(events, "probation_status")
        
        assert status == "critical"


class TestActionDetermineProbationLevel:
    """Tests for ActionDetermineProbationLevel action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionDetermineProbationLevel()
        assert action.name() == "action_determine_probation_level"

    def test_first_probation_p1(self, dispatcher, domain):
        """UT-053: First probation is P1."""
        tracker = create_tracker(slots={"previous_probation_status": "none"})
        action = ActionDetermineProbationLevel()
        
        events = action.run(dispatcher, tracker, domain)
        level = get_slot_value(events, "probation_level")
        
        assert level == "P1"

    def test_after_p1_becomes_p2(self, dispatcher, domain):
        """UT-054: After P1 becomes P2."""
        tracker = create_tracker(slots={"previous_probation_status": "P1"})
        action = ActionDetermineProbationLevel()
        
        events = action.run(dispatcher, tracker, domain)
        level = get_slot_value(events, "probation_level")
        
        assert level == "P2"

    def test_after_p2_becomes_p3(self, dispatcher, domain):
        """UT-055: After P2 becomes P3."""
        tracker = create_tracker(slots={"previous_probation_status": "P2"})
        action = ActionDetermineProbationLevel()
        
        events = action.run(dispatcher, tracker, domain)
        level = get_slot_value(events, "probation_level")
        
        assert level == "P3"


class TestActionResetForAssessment:
    """Tests for ActionResetForAssessment action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionResetForAssessment()
        assert action.name() == "action_reset_for_assessment"

    def test_resets_all_probation_slots(self, dispatcher, domain):
        """Resets all probation-related slots."""
        tracker = create_tracker(slots={
            "current_cgpa": 1.5,
            "probation_status": "probation"
        })
        action = ActionResetForAssessment()
        
        events = action.run(dispatcher, tracker, domain)
        
        cgpa = get_slot_value(events, "current_cgpa")
        status = get_slot_value(events, "probation_status")
        
        assert cgpa is None
        assert status is None

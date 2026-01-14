"""
Tests for admin module actions.

Tests:
- ActionCheckTransferChoice
- ActionAssessTransferEligibility
- ActionCheckChangeChoice
- ActionAssessChangeEligibility
- ActionProvideDeadlineInfo
- ActionAssessFullClassOptions
- ActionAssessClashResolution
- ActionProvideRepeatGuidance
"""

import pytest
from tests.helpers import create_tracker, get_slot_value

from actions.admin.medium_priority_actions import (
    ActionCheckTransferChoice,
    ActionAssessTransferEligibility,
    ActionCheckChangeChoice,
    ActionAssessChangeEligibility,
    ActionProvideDeadlineInfo,
    ActionAssessFullClassOptions,
    ActionAssessClashResolution,
    ActionProvideRepeatGuidance,
)


class TestActionCheckTransferChoice:
    """Tests for ActionCheckTransferChoice action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckTransferChoice()
        assert action.name() == "action_check_transfer_choice"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events."""
        tracker = create_tracker(slots={})
        action = ActionCheckTransferChoice()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionAssessTransferEligibility:
    """Tests for ActionAssessTransferEligibility action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessTransferEligibility()
        assert action.name() == "action_assess_transfer_eligibility"

    def test_eligible_diploma_semester_1(self, dispatcher, domain):
        """UT-064: Eligible (diploma graduate, semester 1)."""
        tracker = create_tracker(slots={
            "student_type": "diploma_graduate",
            "current_semester": 1
        })
        action = ActionAssessTransferEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "transfer_eligible")
        status = get_slot_value(events, "transfer_status")
        
        assert eligible is True
        assert status == "eligible"

    def test_late_diploma_semester_3(self, dispatcher, domain):
        """UT-065: Late (diploma graduate, semester 3+)."""
        tracker = create_tracker(slots={
            "student_type": "diploma_graduate",
            "current_semester": 3
        })
        action = ActionAssessTransferEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "transfer_eligible")
        status = get_slot_value(events, "transfer_status")
        
        assert eligible is False
        assert status == "late"

    def test_not_eligible_regular_student(self, dispatcher, domain):
        """UT-066: Not eligible (regular student)."""
        tracker = create_tracker(slots={
            "student_type": "regular",
            "current_semester": 1
        })
        action = ActionAssessTransferEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "transfer_eligible")
        status = get_slot_value(events, "transfer_status")
        
        assert eligible is False
        assert status == "not_eligible"

    def test_transfer_student_eligible(self, dispatcher, domain):
        """Transfer student in semester 1 is eligible."""
        tracker = create_tracker(slots={
            "student_type": "transfer_student",
            "current_semester": 1
        })
        action = ActionAssessTransferEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "transfer_eligible")
        
        assert eligible is True


class TestActionCheckChangeChoice:
    """Tests for ActionCheckChangeChoice action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionCheckChangeChoice()
        assert action.name() == "action_check_change_choice"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events."""
        tracker = create_tracker(slots={})
        action = ActionCheckChangeChoice()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionAssessChangeEligibility:
    """Tests for ActionAssessChangeEligibility action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessChangeEligibility()
        assert action.name() == "action_assess_change_eligibility"

    def test_eligible_good_cgpa_and_semesters(self, dispatcher, domain):
        """UT-067: Eligible (CGPA ≥2.5, semesters ≥1)."""
        tracker = create_tracker(slots={
            "current_cgpa": 3.0,
            "semesters_completed": 2
        })
        action = ActionAssessChangeEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "change_eligible")
        status = get_slot_value(events, "change_status")
        
        assert eligible is True
        assert status == "eligible"

    def test_too_early_semester_0(self, dispatcher, domain):
        """UT-068: Too early (semester 0)."""
        tracker = create_tracker(slots={
            "current_cgpa": 3.5,
            "semesters_completed": 0
        })
        action = ActionAssessChangeEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "change_eligible")
        status = get_slot_value(events, "change_status")
        
        assert eligible is False
        assert status == "early"

    def test_low_cgpa(self, dispatcher, domain):
        """UT-069: Low CGPA (<2.5)."""
        tracker = create_tracker(slots={
            "current_cgpa": 2.0,
            "semesters_completed": 2
        })
        action = ActionAssessChangeEligibility()
        
        events = action.run(dispatcher, tracker, domain)
        eligible = get_slot_value(events, "change_eligible")
        status = get_slot_value(events, "change_status")
        
        assert eligible is False
        assert status == "cgpa_low"


class TestActionProvideDeadlineInfo:
    """Tests for ActionProvideDeadlineInfo action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionProvideDeadlineInfo()
        assert action.name() == "action_provide_deadline_info"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events."""
        tracker = create_tracker(slots={})
        action = ActionProvideDeadlineInfo()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionAssessFullClassOptions:
    """Tests for ActionAssessFullClassOptions action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessFullClassOptions()
        assert action.name() == "action_assess_full_class_options"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events."""
        tracker = create_tracker(slots={})
        action = ActionAssessFullClassOptions()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionAssessClashResolution:
    """Tests for ActionAssessClashResolution action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionAssessClashResolution()
        assert action.name() == "action_assess_clash_resolution"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events."""
        tracker = create_tracker(slots={})
        action = ActionAssessClashResolution()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []


class TestActionProvideRepeatGuidance:
    """Tests for ActionProvideRepeatGuidance action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionProvideRepeatGuidance()
        assert action.name() == "action_provide_repeat_guidance"

    def test_run_returns_empty_events(self, dispatcher, domain):
        """Action returns empty events."""
        tracker = create_tracker(slots={})
        action = ActionProvideRepeatGuidance()
        
        events = action.run(dispatcher, tracker, domain)
        assert events == []

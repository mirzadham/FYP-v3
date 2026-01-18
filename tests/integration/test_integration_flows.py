"""
Integration tests for multi-action conversation flows.

Tests end-to-end action interactions to ensure proper
slot passing and flow execution between actions.
"""

import pytest
from tests.helpers import create_tracker, get_slot_value


class TestCourseToPrerequisiteFlow:
    """Integration tests for course lookup → prerequisite check flow."""

    def test_course_lookup_then_prereq_check(self, dispatcher, domain):
        """IT-001: After getting course details, check prerequisites works."""
        from actions.academic.course_actions import ActionGetCourseDetails
        from actions.academic.prerequisite_actions import ActionCheckPrerequisites
        
        # Step 1: Get course details
        tracker1 = create_tracker(slots={"course_code": "CSC4600"})
        course_action = ActionGetCourseDetails()
        events1 = course_action.run(dispatcher, tracker1, domain)
        
        # Step 2: Check prerequisites with same code
        tracker2 = create_tracker(slots={"course_code": "CSC4600"})
        prereq_action = ActionCheckPrerequisites()
        events2 = prereq_action.run(dispatcher, tracker2, domain)
        
        # Both actions should complete without error
        assert isinstance(events1, list)
        assert isinstance(events2, list)

    def test_invalid_course_then_prereq_check(self, dispatcher, domain):
        """IT-002: Invalid course code handled gracefully in both actions."""
        from actions.academic.course_actions import ActionGetCourseDetails
        from actions.academic.prerequisite_actions import ActionCheckPrerequisites
        
        tracker = create_tracker(slots={"course_code": "INVALID999"})
        
        course_action = ActionGetCourseDetails()
        events1 = course_action.run(dispatcher, tracker, domain)
        
        prereq_action = ActionCheckPrerequisites()
        events2 = prereq_action.run(dispatcher, tracker, domain)
        
        # Both should handle gracefully
        assert isinstance(events1, list)
        assert isinstance(events2, list)


class TestGraduationAssessmentFlow:
    """Integration tests for graduation requirements flow."""

    def test_check_choice_then_assess_status(self, dispatcher, domain):
        """IT-003: Graduation choice check followed by status assessment."""
        from actions.academic.graduation_actions import (
            ActionCheckGraduationAssessmentChoice,
            ActionAssessGraduationStatus
        )
        
        tracker = create_tracker(slots={
            "assess_choice": "yes",
            "credits_completed": 120
        })
        
        # Step 1: Check if user wants assessment
        choice_action = ActionCheckGraduationAssessmentChoice()
        events1 = choice_action.run(dispatcher, tracker, domain)
        
        # Step 2: Assess graduation status
        assess_action = ActionAssessGraduationStatus()
        events2 = assess_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)

    def test_validate_credits_then_assess(self, dispatcher, domain):
        """IT-004: Credits validation followed by graduation assessment."""
        from actions.academic.graduation_actions import (
            ActionValidateCredits,
            ActionAssessGraduationStatus
        )
        
        # Valid credits
        tracker = create_tracker(slots={"credits_completed": 130})
        
        validate_action = ActionValidateCredits()
        events1 = validate_action.run(dispatcher, tracker, domain)
        
        assess_action = ActionAssessGraduationStatus()
        events2 = assess_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)


class TestProbationAssessmentFlow:
    """Integration tests for probation assessment flow."""

    def test_cgpa_validate_then_assess_probation(self, dispatcher, domain):
        """IT-005: CGPA validation followed by probation assessment."""
        from actions.policies.probation_actions import (
            ActionValidateCgpa,
            ActionAssessProbationStatus
        )
        
        tracker = create_tracker(slots={"current_cgpa": 1.8})
        
        # Step 1: Validate CGPA
        validate_action = ActionValidateCgpa()
        events1 = validate_action.run(dispatcher, tracker, domain)
        
        # Step 2: Assess probation
        assess_action = ActionAssessProbationStatus()
        events2 = assess_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)
        
        # Low CGPA should result in probation-related slot
        probation_status = get_slot_value(events2, "probation_status")
        # Should have some status set (probation or warning)
        assert probation_status is not None

    def test_determine_probation_level(self, dispatcher, domain):
        """IT-006: Full probation level determination flow."""
        from actions.policies.probation_actions import (
            ActionAssessProbationStatus,
            ActionDetermineProbationLevel
        )
        
        tracker = create_tracker(slots={
            "current_cgpa": 1.5,
            "semesters_on_probation": 2
        })
        
        assess_action = ActionAssessProbationStatus()
        events1 = assess_action.run(dispatcher, tracker, domain)
        
        level_action = ActionDetermineProbationLevel()
        events2 = level_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)


class TestGradeAppealFlow:
    """Integration tests for grade appeal assessment flow."""

    def test_validate_days_then_check_deadline(self, dispatcher, domain):
        """IT-007: Days validation followed by deadline check."""
        from actions.policies.grade_appeal_actions import (
            ActionValidateDays,
            ActionCheckAppealDeadline
        )
        
        tracker = create_tracker(slots={"days_since_results": 10})
        
        validate_action = ActionValidateDays()
        events1 = validate_action.run(dispatcher, tracker, domain)
        
        deadline_action = ActionCheckAppealDeadline()
        events2 = deadline_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)

    def test_full_appeal_assessment_flow(self, dispatcher, domain):
        """IT-008: Complete grade appeal assessment flow."""
        from actions.policies.grade_appeal_actions import (
            ActionCheckAppealChoice,
            ActionValidateDays,
            ActionCheckAppealDeadline,
            ActionAssessAppealReadiness
        )
        
        tracker = create_tracker(slots={
            "appeal_choice": "yes",
            "days_since_results": 5
        })
        
        # Run through complete flow
        actions = [
            ActionCheckAppealChoice(),
            ActionValidateDays(),
            ActionCheckAppealDeadline(),
            ActionAssessAppealReadiness()
        ]
        
        for action in actions:
            events = action.run(dispatcher, tracker, domain)
            assert isinstance(events, list)


class TestDropCourseFlow:
    """Integration tests for drop course assessment flow."""

    def test_week_validate_then_assess_consequences(self, dispatcher, domain):
        """IT-009: Week validation followed by consequences assessment."""
        from actions.academic.drop_course_actions import (
            ActionValidateWeek,
            ActionAssessDropConsequences
        )
        
        tracker = create_tracker(slots={"current_week": 5})
        
        validate_action = ActionValidateWeek()
        events1 = validate_action.run(dispatcher, tracker, domain)
        
        assess_action = ActionAssessDropConsequences()
        events2 = assess_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)


class TestIndustrialTrainingFlow:
    """Integration tests for industrial training eligibility flow."""

    def test_year_validate_then_assess_eligibility(self, dispatcher, domain):
        """IT-010: Year validation followed by LI eligibility assessment."""
        from actions.policies.industrial_training_actions import (
            ActionValidateYear,
            ActionAssessLiEligibility
        )
        
        tracker = create_tracker(slots={"current_year": 3})
        
        validate_action = ActionValidateYear()
        events1 = validate_action.run(dispatcher, tracker, domain)
        
        assess_action = ActionAssessLiEligibility()
        events2 = assess_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)


class TestConvocationFlow:
    """Integration tests for convocation eligibility flow."""

    def test_muet_validate_then_assess_eligibility(self, dispatcher, domain):
        """IT-011: MUET validation followed by convocation eligibility."""
        from actions.academic.convocation_actions import (
            ActionValidateMuet,
            ActionAssessConvocationEligibility
        )
        
        tracker = create_tracker(slots={"muet_band": 4})
        
        validate_action = ActionValidateMuet()
        events1 = validate_action.run(dispatcher, tracker, domain)
        
        assess_action = ActionAssessConvocationEligibility()
        events2 = assess_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)


class TestCreditTransferFlow:
    """Integration tests for credit transfer flow."""

    def test_transfer_choice_then_eligibility(self, dispatcher, domain):
        """IT-012: Transfer choice followed by eligibility assessment."""
        from actions.admin.medium_priority_actions import (
            ActionCheckTransferChoice,
            ActionAssessTransferEligibility
        )
        
        tracker = create_tracker(slots={
            "transfer_choice": "yes",
            "student_type": "diploma_graduate",
            "current_semester": 1
        })
        
        choice_action = ActionCheckTransferChoice()
        events1 = choice_action.run(dispatcher, tracker, domain)
        
        eligibility_action = ActionAssessTransferEligibility()
        events2 = eligibility_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)


class TestErrorPropagation:
    """Tests for error handling across action chains."""

    def test_none_slots_handled_across_actions(self, dispatcher, domain):
        """IT-013: None slots don't crash subsequent actions."""
        from actions.academic.course_actions import ActionGetCourseDetails
        from actions.academic.prerequisite_actions import ActionCheckPrerequisites
        
        # Tracker with no slots set
        tracker = create_tracker(slots={})
        
        course_action = ActionGetCourseDetails()
        prereq_action = ActionCheckPrerequisites()
        
        # Should handle gracefully, not crash
        try:
            events1 = course_action.run(dispatcher, tracker, domain)
            events2 = prereq_action.run(dispatcher, tracker, domain)
            assert isinstance(events1, list)
            assert isinstance(events2, list)
        except Exception as e:
            # Document that it failed - this is a potential issue
            pytest.fail(f"Action chain failed with None slots: {e}")

    def test_invalid_input_recovery(self, dispatcher, domain):
        """IT-014: Invalid inputs in flow don't prevent subsequent actions."""
        from actions.academic.graduation_actions import (
            ActionValidateCredits,
            ActionAssessGraduationStatus
        )
        
        # Invalid credits (negative)
        tracker = create_tracker(slots={"credits_completed": -10})
        
        validate_action = ActionValidateCredits()
        assess_action = ActionAssessGraduationStatus()
        
        # Should handle invalid input gracefully
        events1 = validate_action.run(dispatcher, tracker, domain)
        events2 = assess_action.run(dispatcher, tracker, domain)
        
        assert isinstance(events1, list)
        assert isinstance(events2, list)

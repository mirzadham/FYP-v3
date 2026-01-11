"""
Academic Advisor Chatbot - Custom Actions Package

This package contains modular action classes for the Rasa chatbot.
All actions are imported here and re-exported for Rasa to discover.

Module Structure:
- db_utils.py: Shared database connection and query helpers
- course_actions.py: Course information retrieval actions
- prerequisite_actions.py: Prerequisite checking and validation actions
- convocation_actions.py: Convocation eligibility actions
- probation_actions.py: Academic probation assessment actions
- graduation_actions.py: Graduation requirements assessment actions
- industrial_training_actions.py: Industrial training eligibility actions
- drop_course_actions.py: Course drop/withdrawal actions
- grade_appeal_actions.py: Grade appeal guidance actions
- medium_priority_actions.py: Credit transfer, change program, registration actions
- openai_actions.py: RAG-enhanced fallback responses using OpenAI
"""

# Import all action classes for Rasa to discover
from .course_actions import ActionGetCourseDetails
from .prerequisite_actions import (
    ActionCheckPrerequisites,
    ActionValidateCourseCodeFormat,
    ActionResetCourseCode,
)
from .convocation_actions import (
    ActionCheckEligibilityChoice,
    ActionValidateMuet,
    ActionResetMuet,
    ActionAssessConvocationEligibility,
)
from .probation_actions import (
    ActionCheckAssessmentChoice,
    ActionValidateCgpa,
    ActionResetCgpa,
    ActionAssessProbationStatus,
    ActionDetermineProbationLevel,
    ActionResetForAssessment,
)
from .graduation_actions import (
    ActionCheckGraduationAssessmentChoice,
    ActionValidateCredits,
    ActionResetCredits,
    ActionAssessGraduationStatus,
    ActionResetGraduationSlots,
)
from .industrial_training_actions import (
    ActionCheckLiAssessmentChoice,
    ActionValidateYear,
    ActionResetYear,
    ActionAssessLiEligibility,
)
from .drop_course_actions import (
    ActionCheckDropAssessmentChoice,
    ActionValidateWeek,
    ActionResetWeek,
    ActionAssessDropConsequences,
)
from .grade_appeal_actions import (
    ActionCheckAppealChoice,
    ActionValidateDays,
    ActionResetDays,
    ActionCheckAppealDeadline,
    ActionAssessAppealReadiness,
)
from .medium_priority_actions import (
    ActionCheckTransferChoice,
    ActionAssessTransferEligibility,
    ActionCheckChangeChoice,
    ActionAssessChangeEligibility,
    ActionProvideDeadlineInfo,
    ActionAssessFullClassOptions,
    ActionAssessClashResolution,
    ActionProvideRepeatGuidance,
)
from .openai_actions import ActionOpenAIResponse

# Export all actions
__all__ = [
    # Course actions
    "ActionGetCourseDetails",
    "ActionCheckPrerequisites",
    "ActionValidateCourseCodeFormat",
    "ActionResetCourseCode",
    # Convocation actions
    "ActionCheckEligibilityChoice",
    "ActionValidateMuet",
    "ActionResetMuet",
    "ActionAssessConvocationEligibility",
    # Probation actions
    "ActionCheckAssessmentChoice",
    "ActionValidateCgpa",
    "ActionResetCgpa",
    "ActionAssessProbationStatus",
    "ActionDetermineProbationLevel",
    "ActionResetForAssessment",
    # Graduation actions
    "ActionCheckGraduationAssessmentChoice",
    "ActionValidateCredits",
    "ActionResetCredits",
    "ActionAssessGraduationStatus",
    "ActionResetGraduationSlots",
    # Industrial training actions
    "ActionCheckLiAssessmentChoice",
    "ActionValidateYear",
    "ActionResetYear",
    "ActionAssessLiEligibility",
    # Drop course actions
    "ActionCheckDropAssessmentChoice",
    "ActionValidateWeek",
    "ActionResetWeek",
    "ActionAssessDropConsequences",
    # Grade appeal actions
    "ActionCheckAppealChoice",
    "ActionValidateDays",
    "ActionResetDays",
    "ActionCheckAppealDeadline",
    "ActionAssessAppealReadiness",
    # Medium priority actions
    "ActionCheckTransferChoice",
    "ActionAssessTransferEligibility",
    "ActionCheckChangeChoice",
    "ActionAssessChangeEligibility",
    "ActionProvideDeadlineInfo",
    "ActionAssessFullClassOptions",
    "ActionAssessClashResolution",
    "ActionProvideRepeatGuidance",
    # OpenAI actions
    "ActionOpenAIResponse",
]





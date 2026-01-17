"""
Academic Advisor Chatbot - Custom Actions Package

This package contains modular action classes for the Rasa chatbot.
All actions are organized into subfolders and re-exported for Rasa to discover.

Folder Structure:
├── academic/           # Course, prerequisite, graduation, convocation, drop actions
├── policies/           # Probation, industrial training, grade appeal actions
├── admin/              # Registration issues, credit transfer, change program actions
└── system/             # Database utilities and OpenAI fallback actions
"""

# Import from subfolders
from .academic import (
    ActionGetCourseDetails,
    ActionCheckPrerequisites,
    ActionValidateCourseCodeFormat,
    ActionResetCourseCode,
    ActionCheckGraduationAssessmentChoice,
    ActionValidateCredits,
    ActionResetCredits,
    ActionAssessGraduationStatus,
    ActionResetGraduationSlots,
    ActionCheckEligibilityChoice,
    ActionValidateMuet,
    ActionResetMuet,
    ActionAssessConvocationEligibility,
    ActionCheckDropAssessmentChoice,
    ActionValidateWeek,
    ActionResetWeek,
    ActionAssessDropConsequences,
)

from .policies import (
    ActionCheckAssessmentChoice,
    ActionValidateCgpa,
    ActionResetCgpa,
    ActionAssessProbationStatus,
    ActionDetermineProbationLevel,
    ActionResetForAssessment,
    ActionCheckLiAssessmentChoice,
    ActionValidateYear,
    ActionResetYear,
    ActionAssessLiEligibility,
    ActionCheckAppealChoice,
    ActionValidateDays,
    ActionResetDays,
    ActionCheckAppealDeadline,
    ActionAssessAppealReadiness,
)

from .admin import (
    ActionCheckTransferChoice,
    ActionAssessTransferEligibility,
    ActionCheckChangeChoice,
    ActionAssessChangeEligibility,
    ActionProvideDeadlineInfo,
    ActionAssessFullClassOptions,
    ActionAssessClashResolution,
    ActionProvideRepeatGuidance,
)

from .system import (
    get_prerequisites_for_course,
    ActionOpenAIResponse,
)

# Export all actions for Rasa to discover
__all__ = [
    # Academic actions
    "ActionGetCourseDetails",
    "ActionCheckPrerequisites",
    "ActionValidateCourseCodeFormat",
    "ActionResetCourseCode",
    "ActionCheckGraduationAssessmentChoice",
    "ActionValidateCredits",
    "ActionResetCredits",
    "ActionAssessGraduationStatus",
    "ActionResetGraduationSlots",
    "ActionCheckEligibilityChoice",
    "ActionValidateMuet",
    "ActionResetMuet",
    "ActionAssessConvocationEligibility",
    "ActionCheckDropAssessmentChoice",
    "ActionValidateWeek",
    "ActionResetWeek",
    "ActionAssessDropConsequences",
    # Policy actions
    "ActionCheckAssessmentChoice",
    "ActionValidateCgpa",
    "ActionResetCgpa",
    "ActionAssessProbationStatus",
    "ActionDetermineProbationLevel",
    "ActionResetForAssessment",
    "ActionCheckLiAssessmentChoice",
    "ActionValidateYear",
    "ActionResetYear",
    "ActionAssessLiEligibility",
    "ActionCheckAppealChoice",
    "ActionValidateDays",
    "ActionResetDays",
    "ActionCheckAppealDeadline",
    "ActionAssessAppealReadiness",
    # Admin actions
    "ActionCheckTransferChoice",
    "ActionAssessTransferEligibility",
    "ActionCheckChangeChoice",
    "ActionAssessChangeEligibility",
    "ActionProvideDeadlineInfo",
    "ActionAssessFullClassOptions",
    "ActionAssessClashResolution",
    "ActionProvideRepeatGuidance",
    # System utilities
    "get_prerequisites_for_course",
    "ActionOpenAIResponse",
]

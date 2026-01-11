"""
Academic-related actions for Academic Advisor Chatbot.
Handles course information, prerequisites, graduation, convocation, and drop course flows.
"""

from .course_actions import ActionGetCourseDetails
from .prerequisite_actions import (
    ActionCheckPrerequisites,
    ActionValidateCourseCodeFormat,
    ActionResetCourseCode,
)
from .graduation_actions import (
    ActionCheckGraduationAssessmentChoice,
    ActionValidateCredits,
    ActionResetCredits,
    ActionAssessGraduationStatus,
    ActionResetGraduationSlots,
)
from .convocation_actions import (
    ActionCheckEligibilityChoice,
    ActionValidateMuet,
    ActionResetMuet,
    ActionAssessConvocationEligibility,
)
from .drop_course_actions import (
    ActionCheckDropAssessmentChoice,
    ActionValidateWeek,
    ActionResetWeek,
    ActionAssessDropConsequences,
)

__all__ = [
    # Course actions
    "ActionGetCourseDetails",
    # Prerequisite actions
    "ActionCheckPrerequisites",
    "ActionValidateCourseCodeFormat",
    "ActionResetCourseCode",
    # Graduation actions
    "ActionCheckGraduationAssessmentChoice",
    "ActionValidateCredits",
    "ActionResetCredits",
    "ActionAssessGraduationStatus",
    "ActionResetGraduationSlots",
    # Convocation actions
    "ActionCheckEligibilityChoice",
    "ActionValidateMuet",
    "ActionResetMuet",
    "ActionAssessConvocationEligibility",
    # Drop course actions
    "ActionCheckDropAssessmentChoice",
    "ActionValidateWeek",
    "ActionResetWeek",
    "ActionAssessDropConsequences",
]

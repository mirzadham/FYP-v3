"""
Academic Advisor Chatbot - Custom Actions Package

This package contains modular action classes for the Rasa chatbot.
All actions are imported here and re-exported for Rasa to discover.

Module Structure:
- db_utils.py: Shared database connection and query helpers
- course_actions.py: Course information retrieval actions
- prerequisite_actions.py: Prerequisite checking and validation actions
- convocation_actions.py: Convocation information actions
- probation_actions.py: Academic probation assessment actions
- graduation_actions.py: Graduation requirements assessment actions
- openai_actions.py: RAG-enhanced fallback responses using OpenAI
"""

# Import all action classes for Rasa to discover
from .course_actions import ActionGetCourseDetails
from .prerequisite_actions import (
    ActionCheckPrerequisites,
    ActionValidateCourseCodeFormat,
    ActionResetCourseCode,
)
from .convocation_actions import ActionResetConvocationTopic
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
from .openai_actions import ActionOpenAIResponse

# Export all actions
__all__ = [
    "ActionGetCourseDetails",
    "ActionCheckPrerequisites",
    "ActionValidateCourseCodeFormat",
    "ActionResetCourseCode",
    "ActionResetConvocationTopic",
    "ActionCheckAssessmentChoice",
    "ActionValidateCgpa",
    "ActionResetCgpa",
    "ActionAssessProbationStatus",
    "ActionDetermineProbationLevel",
    "ActionResetForAssessment",
    "ActionCheckGraduationAssessmentChoice",
    "ActionValidateCredits",
    "ActionResetCredits",
    "ActionAssessGraduationStatus",
    "ActionResetGraduationSlots",
    "ActionOpenAIResponse",
]



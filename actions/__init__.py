"""
Academic Advisor Chatbot - Custom Actions Package

This package contains modular action classes for the Rasa chatbot.
All actions are imported here and re-exported for Rasa to discover.

Module Structure:
- db_utils.py: Shared database connection and query helpers
- course_actions.py: Course information retrieval actions
- prerequisite_actions.py: Prerequisite checking and validation actions
- openai_actions.py: RAG-enhanced fallback responses using OpenAI
"""

# Import all action classes for Rasa to discover
from .course_actions import ActionGetCourseDetails
from .prerequisite_actions import (
    ActionCheckPrerequisites,
    ActionValidateCourseCodeFormat,
    ActionResetCourseCode,
)
from .openai_actions import ActionOpenAIResponse

# Export all actions
__all__ = [
    "ActionGetCourseDetails",
    "ActionCheckPrerequisites",
    "ActionValidateCourseCodeFormat",
    "ActionResetCourseCode",
    "ActionOpenAIResponse",
]

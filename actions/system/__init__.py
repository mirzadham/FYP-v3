"""
System-level utilities and actions for Academic Advisor Chatbot.
Contains database utilities and OpenAI fallback actions.
"""

from .db_utils import get_db_connection, get_prerequisites_for_course
from .openai_actions import ActionOpenAIResponse

__all__ = [
    "get_db_connection",
    "get_prerequisites_for_course",
    "ActionOpenAIResponse",
]

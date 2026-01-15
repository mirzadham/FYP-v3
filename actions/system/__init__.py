"""
System-level utilities and actions for Academic Advisor Chatbot.
Contains handbook utilities (primary) and OpenAI fallback actions.

Note: db_utils is deprecated and kept for backward compatibility.
      Use handbook_utils for all new code.
"""

from .handbook_utils import (
    get_course_by_code,
    get_prerequisites_for_course,
    semantic_search,
    get_context_for_rag,
    get_course_count,
    get_embedding_count,
)
from .openai_actions import ActionOpenAIResponse

# Deprecated - kept for backward compatibility
from .db_utils import get_db_connection

__all__ = [
    # Primary - use these
    "get_course_by_code",
    "get_prerequisites_for_course",
    "semantic_search",
    "get_context_for_rag",
    "get_course_count",
    "get_embedding_count",
    "ActionOpenAIResponse",
    # Deprecated
    "get_db_connection",
]

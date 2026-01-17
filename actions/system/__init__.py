"""
System-level utilities and actions for Academic Advisor Chatbot.
Contains handbook utilities for course data and OpenAI fallback actions.
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

__all__ = [
    # Primary - use these
    "get_course_by_code",
    "get_prerequisites_for_course",
    "semantic_search",
    "get_context_for_rag",
    "get_course_count",
    "get_embedding_count",
    "ActionOpenAIResponse",
]

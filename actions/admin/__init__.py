"""
Admin-related actions for Academic Advisor Chatbot.
Handles registration issues, class full, timetable clash, credit transfer, etc.
"""

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

__all__ = [
    "ActionCheckTransferChoice",
    "ActionAssessTransferEligibility",
    "ActionCheckChangeChoice",
    "ActionAssessChangeEligibility",
    "ActionProvideDeadlineInfo",
    "ActionAssessFullClassOptions",
    "ActionAssessClashResolution",
    "ActionProvideRepeatGuidance",
]

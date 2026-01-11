"""
Grade appeal actions for Academic Advisor Chatbot.
Handles deadline checking and appeal readiness assessment.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


# Appeal deadline in days
APPEAL_DEADLINE_DAYS = 14


class ActionCheckAppealChoice(Action):
    """Check if user wants appeal assessment."""

    def name(self) -> Text:
        return "action_check_appeal_choice"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return []


class ActionValidateDays(Action):
    """Validate days since results input."""

    def name(self) -> Text:
        return "action_validate_days"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        days = tracker.get_slot("days_since_results")
        
        if days is None:
            return [SlotSet("days_valid", False)]
        
        try:
            if isinstance(days, str):
                days = days.strip().lower().replace("days", "").replace("day", "").strip()
                days_float = float(days)
            else:
                days_float = float(days)
            
            if 0 <= days_float <= 365:
                days_int = int(days_float)
                return [
                    SlotSet("days_since_results", days_int),
                    SlotSet("days_valid", True)
                ]
            else:
                return [SlotSet("days_valid", False)]
                
        except (ValueError, TypeError):
            return [SlotSet("days_valid", False)]


class ActionResetDays(Action):
    """Reset days slot for re-entry."""

    def name(self) -> Text:
        return "action_reset_days"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("days_since_results", None),
            SlotSet("days_valid", None)
        ]


class ActionCheckAppealDeadline(Action):
    """Check if student is within appeal deadline."""

    def name(self) -> Text:
        return "action_check_appeal_deadline"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        days = tracker.get_slot("days_since_results")
        
        try:
            days = int(days) if days else 0
        except (ValueError, TypeError):
            days = 0
        
        within_deadline = days <= APPEAL_DEADLINE_DAYS
        
        return [SlotSet("within_deadline", within_deadline)]


class ActionAssessAppealReadiness(Action):
    """Assess if student should review script first before formal appeal."""

    def name(self) -> Text:
        return "action_assess_appeal_readiness"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        has_reviewed = tracker.get_slot("has_reviewed_script")
        
        # If they haven't reviewed, recommend doing so first
        should_review = not has_reviewed
        
        return [SlotSet("should_review_first", should_review)]

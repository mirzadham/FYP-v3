"""
Deferment actions for Academic Advisor Chatbot.
Handles timing assessment for deferment guidance.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionAssessDefermentTiming(Action):
    """Assess timing for deferment and provide context."""

    def name(self) -> Text:
        return "action_assess_deferment_timing"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Just pass through - timing warning handled separately
        return []


class ActionProvideTimingWarning(Action):
    """
    Check if it's late in semester for deferment.
    Week 4 is typically the latest recommended time.
    """

    def name(self) -> Text:
        return "action_provide_timing_warning"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        week = tracker.get_slot("current_semester_week")
        
        try:
            week = int(week) if week else 1
        except (ValueError, TypeError):
            week = 1
        
        # After week 4 is considered late for deferment
        is_late = week > 4
        
        return [SlotSet("is_late_deferment", is_late)]

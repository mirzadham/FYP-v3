"""
Drop course actions for Academic Advisor Chatbot.
Handles week validation and drop consequence assessment.

UPM Policy: NO refunds for dropping courses after Week 2.
Late drops incur a penalty fee.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionCheckDropAssessmentChoice(Action):
    """Check if user wants drop assessment."""

    def name(self) -> Text:
        return "action_check_drop_assessment_choice"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return []


class ActionValidateWeek(Action):
    """Validate semester week input (1-14)."""

    def name(self) -> Text:
        return "action_validate_week"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        week = tracker.get_slot("current_week")
        
        if week is None:
            return [SlotSet("week_valid", False)]
        
        try:
            if isinstance(week, str):
                week = week.strip().lower().replace("week", "").strip()
                week_float = float(week)
            else:
                week_float = float(week)
            
            if 1 <= week_float <= 14:
                week_int = int(week_float)
                return [
                    SlotSet("current_week", week_int),
                    SlotSet("week_valid", True)
                ]
            else:
                return [SlotSet("week_valid", False)]
                
        except (ValueError, TypeError):
            return [SlotSet("week_valid", False)]


class ActionResetWeek(Action):
    """Reset week slot for re-entry."""

    def name(self) -> Text:
        return "action_reset_week"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("current_week", None),
            SlotSet("week_valid", None)
        ]


class ActionAssessDropConsequences(Action):
    """
    Assess drop consequences based on semester week.
    
    UPM Policy:
    - Week 1-2: free (no penalty, no record)
    - Week 3-7: late (penalty fee, W grade)
    - Week 8-12: very_late (penalty fee, W grade, multiple approvals)
    - Week 13+: closed (cannot drop)
    
    NOTE: UPM does NOT provide refunds for dropping courses.
    Late drops INCUR a penalty fee.
    """

    def name(self) -> Text:
        return "action_assess_drop_consequences"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        week = tracker.get_slot("current_week")
        
        try:
            week = int(week) if week else 14
        except (ValueError, TypeError):
            week = 14
        
        # Determine phase and penalty status
        if week <= 2:
            phase = "free"
            has_penalty = False
        elif week <= 7:
            phase = "late"
            has_penalty = True
        elif week <= 12:
            phase = "very_late"
            has_penalty = True
        else:
            phase = "closed"
            has_penalty = False  # Can't drop, so no penalty applies
        
        return [
            SlotSet("drop_phase", phase),
            SlotSet("has_penalty_fee", has_penalty)
        ]

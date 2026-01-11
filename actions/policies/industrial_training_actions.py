"""
Industrial Training eligibility actions for Academic Advisor Chatbot.
Handles year validation and LI eligibility assessment.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


# Constants for LI eligibility
MIN_YEAR_FOR_LI = 3
MIN_CREDITS_FOR_LI = 70


class ActionCheckLiAssessmentChoice(Action):
    """Check if user wants LI eligibility assessment."""

    def name(self) -> Text:
        return "action_check_li_assessment_choice"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return []


class ActionValidateYear(Action):
    """
    Validate year of study input.
    Valid range: 1-4 (or 5 for extended programs)
    """

    def name(self) -> Text:
        return "action_validate_year"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        year = tracker.get_slot("current_year")
        
        if year is None:
            return [SlotSet("year_valid", False)]
        
        try:
            if isinstance(year, str):
                year = year.strip().lower()
                # Handle text like "year 3" or "3rd year"
                year = year.replace("year", "").replace("st", "").replace("nd", "").replace("rd", "").replace("th", "").strip()
                year_float = float(year)
            else:
                year_float = float(year)
            
            # Valid range 1-5
            if 1 <= year_float <= 5:
                year_int = int(year_float)
                return [
                    SlotSet("current_year", year_int),
                    SlotSet("year_valid", True)
                ]
            else:
                return [SlotSet("year_valid", False)]
                
        except (ValueError, TypeError):
            return [SlotSet("year_valid", False)]


class ActionResetYear(Action):
    """Reset year slot for re-entry."""

    def name(self) -> Text:
        return "action_reset_year"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("current_year", None),
            SlotSet("year_valid", None)
        ]


class ActionAssessLiEligibility(Action):
    """
    Assess industrial training eligibility based on:
    1. Year >= 3
    2. Credits >= 70
    3. Not on probation
    """

    def name(self) -> Text:
        return "action_assess_li_eligibility"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        year = tracker.get_slot("current_year")
        credits = tracker.get_slot("credits_completed")
        on_probation = tracker.get_slot("is_on_probation")
        
        # Convert with defaults
        try:
            year = int(year) if year else 1
            credits = float(credits) if credits else 0
        except (ValueError, TypeError):
            year = 1
            credits = 0
        
        # Track issues
        issues = []
        eligible = True
        status = "eligible"
        
        # Check year
        if year < MIN_YEAR_FOR_LI:
            eligible = False
            status = "not_yet"
            issues.append(f"⏰ **Year:** Currently Year {year} (LI typically in Year 3-4)")
        
        # Check credits
        if credits < MIN_CREDITS_FOR_LI:
            if status != "not_yet":
                eligible = False
                status = "not_eligible"
            issues.append(f"📚 **Credits:** {credits} completed (minimum ~{MIN_CREDITS_FOR_LI} needed)")
        
        # Check probation
        if on_probation:
            eligible = False
            status = "not_eligible"
            issues.append("⚠️ **Probation:** Cannot do LI while on academic probation")
        
        # Format issues
        if issues:
            issues_text = "\n".join(issues)
        else:
            issues_text = "All requirements met! ✅"
        
        return [
            SlotSet("li_eligible", eligible),
            SlotSet("li_status", status),
            SlotSet("li_issues", issues_text)
        ]

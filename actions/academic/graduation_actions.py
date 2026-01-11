"""
Graduation-related actions for Academic Advisor Chatbot.
Handles credit validation and graduation status assessment via self-assessment.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


# Constants for graduation requirements
BACHELOR_TOTAL_CREDITS = 120
DIPLOMA_TOTAL_CREDITS = 90
CREDITS_PER_SEMESTER = 15


class ActionCheckGraduationAssessmentChoice(Action):
    """
    Check if user wants personalized graduation assessment or just general info.
    """

    def name(self) -> Text:
        return "action_check_graduation_assessment_choice"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # The slot is already set by from_llm mapping
        return []


class ActionValidateCredits(Action):
    """
    Validate that the provided credit count is in correct format and reasonable range.
    Credits should be a positive number, typically 0-150 for bachelor's.
    Sets credits_valid slot to True/False.
    """

    def name(self) -> Text:
        return "action_validate_credits"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        credits = tracker.get_slot("credits_completed")
        
        # Check if credits provided
        if credits is None:
            return [SlotSet("credits_valid", False)]
        
        try:
            # Convert to float if string
            if isinstance(credits, str):
                credits = credits.strip()
                credits_float = float(credits)
            else:
                credits_float = float(credits)
            
            # Validate range (0 to 150 is reasonable)
            if 0 <= credits_float <= 150:
                # Round to whole number for credits
                credits_int = int(round(credits_float))
                return [
                    SlotSet("credits_completed", credits_int),
                    SlotSet("credits_valid", True)
                ]
            else:
                return [SlotSet("credits_valid", False)]
                
        except (ValueError, TypeError) as e:
            print(f"Credits validation error: {e}")
            return [SlotSet("credits_valid", False)]


class ActionResetCredits(Action):
    """
    Reset credits slot to allow user to re-enter.
    """

    def name(self) -> Text:
        return "action_reset_credits"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("credits_completed", None),
            SlotSet("credits_valid", None)
        ]


class ActionAssessGraduationStatus(Action):
    """
    Assess graduation status based on credits, CGPA, and program type.
    
    Status Categories:
    - eligible: Credits >= required AND CGPA >= 2.0
    - close: Within 20 credits of requirement
    - in_progress: 40-100 credits (Year 2-3)
    - early_stage: Less than 40 credits (Year 1)
    
    Also calculates remaining credits and estimated semesters.
    """

    def name(self) -> Text:
        return "action_assess_graduation_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        credits = tracker.get_slot("credits_completed")
        cgpa = tracker.get_slot("current_cgpa")
        program = tracker.get_slot("program_type")
        
        # Default to bachelor if not specified
        if program == "diploma":
            total_required = DIPLOMA_TOTAL_CREDITS
        else:
            total_required = BACHELOR_TOTAL_CREDITS
        
        # Handle missing values
        if credits is None:
            credits = 0
        if cgpa is None:
            cgpa = 2.0  # Assume passing if not provided
            
        try:
            credits = float(credits)
            cgpa = float(cgpa)
        except (ValueError, TypeError):
            credits = 0
            cgpa = 2.0
        
        # Calculate remaining credits
        remaining = max(0, total_required - credits)
        
        # Calculate estimated semesters (assuming 15 credits/semester)
        if remaining > 0:
            estimated_semesters = round(remaining / CREDITS_PER_SEMESTER, 1)
        else:
            estimated_semesters = 0
        
        # Determine status
        if credits >= total_required and cgpa >= 2.0:
            status = "eligible"
        elif remaining <= 20:  # Within 20 credits
            status = "close"
        elif credits >= 40:  # Year 2-3 range
            status = "in_progress"
        else:  # Less than 40 credits
            status = "early_stage"
        
        return [
            SlotSet("graduation_status", status),
            SlotSet("credits_remaining", remaining),
            SlotSet("estimated_semesters", estimated_semesters)
        ]


class ActionResetGraduationSlots(Action):
    """
    Reset all graduation-related slots for a fresh assessment.
    """

    def name(self) -> Text:
        return "action_reset_graduation_slots"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("credits_completed", None),
            SlotSet("credits_valid", None),
            SlotSet("current_cgpa", None),
            SlotSet("cgpa_valid", None),
            SlotSet("program_type", None),
            SlotSet("graduation_status", None),
            SlotSet("credits_remaining", None),
            SlotSet("estimated_semesters", None),
            SlotSet("wants_graduation_assessment", True)
        ]

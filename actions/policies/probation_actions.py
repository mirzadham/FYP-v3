"""
Probation-related actions for Academic Advisor Chatbot.
Handles CGPA validation and probation status assessment via self-assessment.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionCheckAssessmentChoice(Action):
    """
    Check if user wants personalized assessment or just general info.
    Sets a flag based on user's choice.
    """

    def name(self) -> Text:
        return "action_check_assessment_choice"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This action just confirms the choice was registered
        # The slot is already set by from_llm mapping
        return []


class ActionValidateCgpa(Action):
    """
    Validate that the provided CGPA is in correct format and range.
    CGPA must be a number between 0.00 and 4.00.
    Sets cgpa_valid slot to True/False.
    """

    def name(self) -> Text:
        return "action_validate_cgpa"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        cgpa = tracker.get_slot("current_cgpa")
        
        # Check if CGPA is provided
        if cgpa is None:
            return [SlotSet("cgpa_valid", False)]
        
        try:
            # Convert to float if string
            if isinstance(cgpa, str):
                # Handle common formats like "2.5", "2,5", "2.50"
                cgpa = cgpa.replace(",", ".").strip()
                cgpa_float = float(cgpa)
            else:
                cgpa_float = float(cgpa)
            
            # Validate range (0.00 to 4.00)
            if 0.0 <= cgpa_float <= 4.0:
                # Round to 2 decimal places for consistency
                cgpa_float = round(cgpa_float, 2)
                return [
                    SlotSet("current_cgpa", cgpa_float),
                    SlotSet("cgpa_valid", True)
                ]
            else:
                return [SlotSet("cgpa_valid", False)]
                
        except (ValueError, TypeError) as e:
            print(f"CGPA validation error: {e}")
            return [SlotSet("cgpa_valid", False)]


class ActionResetCgpa(Action):
    """
    Reset CGPA slot to allow user to re-enter their CGPA.
    """

    def name(self) -> Text:
        return "action_reset_cgpa"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("current_cgpa", None),
            SlotSet("cgpa_valid", None)
        ]


class ActionAssessProbationStatus(Action):
    """
    Assess probation status based on CGPA value.
    
    Status Categories:
    - not_on_probation: CGPA >= 2.00
    - warning: CGPA 1.80 - 1.99 (close to probation)
    - probation: CGPA 1.50 - 1.79 (on probation)
    - critical: CGPA < 1.50 (severe academic difficulty)
    """

    def name(self) -> Text:
        return "action_assess_probation_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        cgpa = tracker.get_slot("current_cgpa")
        
        if cgpa is None:
            return [SlotSet("probation_status", "critical")]
        
        try:
            cgpa_float = float(cgpa)
            
            if cgpa_float >= 2.0:
                status = "not_on_probation"
            elif cgpa_float >= 1.80:
                status = "warning"
            elif cgpa_float >= 1.50:
                status = "probation"
            else:
                status = "critical"
            
            return [SlotSet("probation_status", status)]
            
        except (ValueError, TypeError):
            return [SlotSet("probation_status", "critical")]


class ActionDetermineProbationLevel(Action):
    """
    Determine the probation level (P1, P2, P3) based on current CGPA
    and previous semester probation history.
    
    Logic:
    - If previous was 'none' (not on probation) -> P1
    - If previous was 'P1' -> P2
    - If previous was 'P2' -> P3
    """

    def name(self) -> Text:
        return "action_determine_probation_level"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        previous_status = tracker.get_slot("previous_probation_status")
        
        # Normalize input
        if previous_status:
            previous_status = str(previous_status).upper().strip()
        
        # Determine current probation level
        if previous_status in ["P2", "2"]:
            level = "P3"
        elif previous_status in ["P1", "1"]:
            level = "P2"
        else:
            # First time on probation or unknown history
            level = "P1"
        
        return [SlotSet("probation_level", level)]


class ActionResetForAssessment(Action):
    """
    Reset all probation-related slots to start a fresh assessment.
    """

    def name(self) -> Text:
        return "action_reset_for_assessment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("current_cgpa", None),
            SlotSet("cgpa_valid", None),
            SlotSet("probation_status", None),
            SlotSet("previous_probation_status", None),
            SlotSet("probation_level", None),
            SlotSet("wants_probation_assessment", True)
        ]

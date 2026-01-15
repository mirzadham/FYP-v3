"""
Course-related actions for Academic Advisor Chatbot.
Handles course information retrieval from faculty handbooks.
Includes validation, follow-up options, and reset functionality.
"""

import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from ..system.handbook_utils import get_course_by_code, get_prerequisites_for_course


class ActionValidateCourseCodeFormat(Action):
    """
    Validate course code format.
    Expected format: 3-4 letters + 4 digits (e.g., CCS3101, CSC4600, SSK3100)
    """

    def name(self) -> Text:
        return "action_validate_course_code_format"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        course_code = tracker.get_slot("course_code")
        
        if not course_code:
            return [SlotSet("course_code_valid", False)]
        
        # Normalize: uppercase, strip whitespace
        code = course_code.upper().strip()
        
        # Pattern: 3-4 letters followed by 4 digits
        pattern = r'^[A-Z]{3,4}\d{4}$'
        
        if re.match(pattern, code):
            return [
                SlotSet("course_code", code),
                SlotSet("course_code_valid", True)
            ]
        else:
            return [SlotSet("course_code_valid", False)]


class ActionResetCourseCode(Action):
    """Reset course code slot for re-entry."""

    def name(self) -> Text:
        return "action_reset_course_code"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("course_code", None),
            SlotSet("course_code_valid", None)
        ]


class ActionResetCourseSlots(Action):
    """Reset all course-related slots for a new search."""

    def name(self) -> Text:
        return "action_reset_course_slots"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("course_code", None),
            SlotSet("course_code_valid", None),
            SlotSet("course_name", None),
            SlotSet("credits", None),
            SlotSet("synopsis", None),
            SlotSet("prereq_list", None),
            SlotSet("wants_course_followup", None),
            SlotSet("course_followup_type", None),
            SlotSet("wants_another_course", None),
            SlotSet("return_value", None),
        ]


class ActionGetCourseDetails(Action):
    """
    Get detailed information about a course from the handbook data.
    
    Retrieves course code, name (English/Malay), credit hours, 
    description, and prerequisites from extracted PDF data.
    Sets return_value slot to 'course_found' or 'course_not_found'.
    """

    def name(self) -> Text:
        return "get_course_details"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        course_code = tracker.get_slot("course_code")
        
        if not course_code:
            return [SlotSet("return_value", "course_not_found")]
        
        # Normalize course code
        course_code = course_code.upper().strip()
        
        try:
            # Get course from handbook data
            course = get_course_by_code(course_code)
            
            if course:
                code = course.get("course_code", course_code)
                # Prefer English name, fallback to Malay
                name = course.get("course_name_english") or course.get("course_name_malay") or "Unknown"
                credits = course.get("credits", "N/A")
                # Prefer English description, fallback to Malay
                description = course.get("description_english") or course.get("description_malay") or "No description available."
                
                # Get prerequisites
                prereq_list = get_prerequisites_for_course(code)
                prereq_str = ", ".join(prereq_list) if prereq_list else "None"
                
                return [
                    SlotSet("course_code", code),
                    SlotSet("course_name", name),
                    SlotSet("credits", credits),
                    SlotSet("synopsis", description),
                    SlotSet("prereq_list", prereq_str),
                    SlotSet("return_value", "course_found"),
                ]
            else:
                return [
                    SlotSet("course_code", course_code),
                    SlotSet("return_value", "course_not_found")
                ]
                
        except Exception as e:
            print(f"Error in get_course_details: {e}")
            return [SlotSet("return_value", "database_error")]


class ActionProvideCourseFollowup(Action):
    """
    Provide follow-up information based on what the student requested.
    Options: prerequisites, schedule, similar_courses
    """

    def name(self) -> Text:
        return "action_provide_course_followup"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        followup_type = tracker.get_slot("course_followup_type")
        course_code = tracker.get_slot("course_code")
        prereq_list = tracker.get_slot("prereq_list")
        
        if followup_type == "prerequisites":
            dispatcher.utter_message(response="utter_followup_prerequisites")
        elif followup_type == "schedule":
            dispatcher.utter_message(response="utter_followup_schedule")
        elif followup_type == "similar_courses":
            dispatcher.utter_message(response="utter_followup_similar")
        else:
            # Default to prerequisites if unclear
            dispatcher.utter_message(response="utter_followup_prerequisites")
        
        return []

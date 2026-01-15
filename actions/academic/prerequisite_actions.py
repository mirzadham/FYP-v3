"""
Prerequisite-related actions for Academic Advisor Chatbot.
Handles prerequisite checking, validation, and reset operations.
"""

import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from ..system.handbook_utils import get_course_by_code, get_prerequisites_for_course


class ActionCheckPrerequisites(Action):
    """
    Check prerequisites for a course from the handbook data.
    
    Returns:
        - return_value: 'course_found' | 'course_not_found' | 'database_error'
        - has_prerequisites: True/False
        - prereq_list: Formatted prerequisite list or "None"
        - course_name: Name of the course
    """

    def name(self) -> Text:
        return "check_prerequisites"

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
            
            if not course:
                return [
                    SlotSet("course_code", course_code),
                    SlotSet("return_value", "course_not_found")
                ]
            
            code = course.get("course_code", course_code)
            # Prefer English name, fallback to Malay
            name = course.get("course_name_english") or course.get("course_name_malay") or "Unknown"
            
            # Get prerequisites
            prereq_list = get_prerequisites_for_course(code)
            has_prereqs = len(prereq_list) > 0
            prereq_str = ", ".join(prereq_list) if prereq_list else "None"
            
            return [
                SlotSet("course_code", code),
                SlotSet("course_name", name),
                SlotSet("prereq_list", prereq_str),
                SlotSet("has_prerequisites", has_prereqs),
                SlotSet("return_value", "course_found"),
            ]
                
        except Exception as e:
            print(f"Error in check_prerequisites: {e}")
            return [SlotSet("return_value", "database_error")]


class ActionValidateCourseCodeFormat(Action):
    """
    Validates that the course_code slot contains a properly formatted
    UPM course code (3 uppercase letters + 4 digits).
    
    Sets slot 'course_code_valid' to True/False.
    """

    def name(self) -> Text:
        return "validate_course_code_format"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        course_code = tracker.get_slot("course_code")
        
        if not course_code:
            return [SlotSet("course_code_valid", False)]
        
        # UPM course code pattern: 3 letters + 4 digits
        pattern = r'^[A-Za-z]{3}[0-9]{4}$'
        is_valid = bool(re.match(pattern, course_code.strip()))
        
        return [SlotSet("course_code_valid", is_valid)]


class ActionResetCourseCode(Action):
    """
    Resets the course_code and related slots to None, allowing the flow
    to collect a new course code from the student.
    """

    def name(self) -> Text:
        return "reset_course_code"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("course_code", None),
            SlotSet("course_code_valid", None),
            SlotSet("has_prerequisites", None),
            SlotSet("prereq_list", None),
            SlotSet("wants_another_check", None),
        ]

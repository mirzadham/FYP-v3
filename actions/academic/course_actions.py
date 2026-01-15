"""
Course-related actions for Academic Advisor Chatbot.
Handles course information retrieval from faculty handbooks.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from ..system.handbook_utils import get_course_by_code, get_prerequisites_for_course


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


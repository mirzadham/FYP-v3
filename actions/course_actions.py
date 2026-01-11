"""
Course-related actions for Academic Advisor Chatbot.
Handles course information retrieval.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .db_utils import get_db_connection, get_prerequisites_for_course


class ActionGetCourseDetails(Action):
    """
    Get detailed information about a course from the academic database.
    
    Retrieves course code, name, credit hours, description, and prerequisites.
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
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query course details from courses table
            cursor.execute("""
                SELECT course_code, course_name, credit_hours, description
                FROM courses
                WHERE UPPER(course_code) = ?
            """, (course_code,))
            
            result = cursor.fetchone()
            
            if result:
                code, name, credits, description = result
                
                # Get prerequisites
                prereq_list = get_prerequisites_for_course(code, cursor)
                if not prereq_list:
                    prereq_list = "None"
                
                conn.close()
                
                return [
                    SlotSet("course_code", code),
                    SlotSet("course_name", name),
                    SlotSet("credits", credits),
                    SlotSet("synopsis", description),
                    SlotSet("prereq_list", prereq_list),
                    SlotSet("return_value", "course_found"),
                ]
            else:
                conn.close()
                return [
                    SlotSet("course_code", course_code),
                    SlotSet("return_value", "course_not_found")
                ]
                
        except Exception as e:
            print(f"Database error in get_course_details: {e}")
            return [SlotSet("return_value", "database_error")]

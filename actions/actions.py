"""
Custom actions for Academic Advisor Chatbot.
Queries the academic.db SQLite database for course information.

Database Schema:
- courses: course_code (PK), course_name, credit_hours, description
- prerequisites: course_code, prereq_code
"""

import sqlite3
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from openai import OpenAI


# Database path - relative to the project root
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "academic.db")


def get_db_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def get_prerequisites_for_course(course_code: str, cursor) -> str:
    """Query prerequisites for a given course code."""
    cursor.execute("""
        SELECT c.course_name, p.prereq_code
        FROM prerequisites p
        JOIN courses c ON c.course_code = p.prereq_code
        WHERE UPPER(p.course_code) = ?
    """, (course_code.upper(),))
    
    prereqs = cursor.fetchall()
    
    if prereqs:
        prereq_list = [f"• {code}: {name}" for name, code in prereqs]
        return "\n".join(prereq_list)
    return None


class ActionGetCourseDetails(Action):
    """Get detailed information about a course."""

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
                    SlotSet("synopsis", description),  # Map description to synopsis slot
                    SlotSet("prereq_list", prereq_list),
                    SlotSet("return_value", "course_found"),
                ]
            else:
                conn.close()
                return [SlotSet("return_value", "course_not_found")]
                
        except Exception as e:
            print(f"Database error in get_course_details: {e}")
            return [SlotSet("return_value", "course_not_found")]


class ActionCheckPrerequisites(Action):
    """Check prerequisites for a course."""

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
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # First check if course exists
            cursor.execute("""
                SELECT course_code, course_name
                FROM courses
                WHERE UPPER(course_code) = ?
            """, (course_code,))
            
            course = cursor.fetchone()
            
            if not course:
                conn.close()
                return [SlotSet("return_value", "course_not_found")]
            
            code, name = course
            
            # Get prerequisites
            prereq_list = get_prerequisites_for_course(code, cursor)
            has_prereqs = prereq_list is not None
            
            if not prereq_list:
                prereq_list = "None"
            
            conn.close()
            
            return [
                SlotSet("course_code", code),
                SlotSet("course_name", name),
                SlotSet("prereq_list", prereq_list),
                SlotSet("has_prerequisites", has_prereqs),
                SlotSet("return_value", "course_found"),
            ]
                
        except Exception as e:
            print(f"Database error in check_prerequisites: {e}")
            return [SlotSet("return_value", "course_not_found")]


class ActionOpenAIResponse(Action):
    """
    RAG-enhanced fallback response using OpenAI.
    Handles queries that don't match any specific flow.
    """

    def name(self) -> Text:
        return "action_openai_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get the last user message
        user_message = tracker.latest_message.get("text", "")
        
        if not user_message:
            dispatcher.utter_message(
                text="I'm not sure what you're asking. Could you please rephrase your question?"
            )
            return []
        
        try:
            # Query knowledge base for context
            context = self._get_relevant_context(user_message)
            
            # Create OpenAI client (uses OPENAI_API_KEY env variable)
            client = OpenAI()
            
            # Generate response with context
            system_prompt = """You are an Academic Advisor chatbot for Universiti Putra Malaysia (UPM).
You help students with academic queries, course information, policies, and general university guidance.
Be helpful, accurate, and concise. If you don't know something, say so.
Always be friendly and supportive to students.

Use the following context from the UPM academic database to answer questions:
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt + context},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            dispatcher.utter_message(text=answer)
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            dispatcher.utter_message(
                text="I'm having trouble processing your request right now. "
                     "Please try again or contact the academic office for assistance."
            )
        
        return []
    
    def _get_relevant_context(self, query: str) -> str:
        """Retrieve relevant context from the knowledge base."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Search for relevant courses based on keywords
            keywords = [kw for kw in query.lower().split() if len(kw) > 3][:5]
            
            results = []
            for keyword in keywords:
                # Search in course names and descriptions
                cursor.execute("""
                    SELECT course_code, course_name, description
                    FROM courses
                    WHERE LOWER(course_name) LIKE ? OR LOWER(description) LIKE ?
                    LIMIT 3
                """, (f"%{keyword}%", f"%{keyword}%"))
                results.extend(cursor.fetchall())
            
            conn.close()
            
            # Deduplicate and format
            unique_courses = {}
            for code, name, desc in results:
                if code not in unique_courses:
                    unique_courses[code] = f"**{code}**: {name}\n{desc[:200]}..."
            
            if unique_courses:
                return "\n\n".join(list(unique_courses.values())[:5])
            return "No specific course information found in the database."
            
        except Exception as e:
            print(f"Context retrieval error: {e}")
            return "Unable to retrieve context from the database."

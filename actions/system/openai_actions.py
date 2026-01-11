"""
OpenAI-powered actions for Academic Advisor Chatbot.
RAG-enhanced fallback responses using OpenAI GPT.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from openai import OpenAI

from .db_utils import get_db_connection


class ActionOpenAIResponse(Action):
    """
    RAG-enhanced fallback response using OpenAI.
    Handles queries that don't match any specific flow.
    
    Retrieves relevant context from the course database and
    generates an appropriate academic advisor response.
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
Your ONLY purpose is to help with:
- Course information, prerequisites, and registration
- Academic policies and procedures
- University deadlines and requirements
- Student support services

IMPORTANT RULES:
1. If a question is NOT related to UPM academics, politely decline: "I can only help with academic matters at UPM."
2. Never provide: legal advice, medical advice, financial advice, or help with anything unethical/illegal.
3. If unsure whether you can help, redirect to the appropriate university department.
4. Be helpful, accurate, and concise for valid academic queries.

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
        """
        Retrieve relevant context from the knowledge base.
        
        Args:
            query: The user's query to find context for
            
        Returns:
            Formatted context string for the LLM prompt
        """
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

"""
OpenAI-powered actions for Academic Advisor Chatbot.
RAG-enhanced fallback responses using OpenAI GPT with semantic search.

Supports multiple knowledge domains:
- Courses: Course information, prerequisites, syllabi
- Calendar: Academic calendar, dates, deadlines
- Rules: Academic policies, CGPA, probation, graduation
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from openai import OpenAI

from .handbook_utils import get_context_for_rag


class ActionOpenAIResponse(Action):
    """
    RAG-enhanced fallback response using OpenAI.
    Handles queries that don't match any specific flow.
    
    Uses LLM-based intent detection to determine query domain,
    then retrieves relevant context from the appropriate knowledge base.
    """

    def name(self) -> Text:
        return "action_openai_response"

    def _detect_query_domain(self, client: OpenAI, query: str) -> str:
        """
        Use LLM to classify query into courses, calendar, rules, or all.
        
        Args:
            client: OpenAI client instance
            query: User's query text
            
        Returns:
            Domain string: "courses", "calendar", "rules", or "all"
        """
        classification_prompt = f"""Classify this academic query into ONE category:
- COURSES: About specific courses, prerequisites, syllabi, course codes (e.g., CCS3001)
- CALENDAR: About dates, deadlines, semester schedules, registration periods, exam dates
- RULES: About academic policies, CGPA calculation, probation, graduation requirements, appeals
- ALL: General/unclear queries that may need multiple sources

Query: {query}

Respond with ONLY one word: COURSES, CALENDAR, RULES, or ALL"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0,
                max_tokens=10
            )
            
            domain = response.choices[0].message.content.strip().lower()
            
            # Validate response
            if domain in ["courses", "calendar", "rules", "all"]:
                return domain
            return "all"
            
        except Exception as e:
            print(f"Intent detection error: {e}")
            return "all"

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
            # Create OpenAI client (uses OPENAI_API_KEY env variable)
            client = OpenAI()
            
            # Detect query domain using LLM
            query_domain = self._detect_query_domain(client, user_message)
            print(f"🎯 Detected query domain: {query_domain}")
            
            # Use semantic search to find relevant context from the detected domain
            context = get_context_for_rag(user_message, top_k=3, domain=query_domain)
            
            # Generate response with context
            system_prompt = """You are an Academic Advisor chatbot for Universiti Putra Malaysia (UPM).
Your ONLY purpose is to help with:
- Course information, prerequisites, and registration
- Academic policies and procedures (from the Academic Rules handbook)
- University calendar, deadlines, and important dates
- Student support services

You have access to THREE knowledge sources:
1. COURSE DATABASE: Details on all UPM courses, prerequisites, credits
2. ACADEMIC RULES: Regulations on CGPA calculation, probation, graduation, appeals
3. ACADEMIC CALENDAR: Semester dates, registration periods, exam schedules

IMPORTANT RULES:
1. If a question is NOT related to UPM academics, politely decline: "I can only help with academic matters at UPM."
2. Never provide: legal advice, medical advice, financial advice, or help with anything unethical/illegal.
3. If unsure whether you can help, redirect to the appropriate university department.
4. Be helpful, accurate, and concise for valid academic queries.
5. When mentioning courses, include both the course code and name.
6. You may respond in English or Malay based on the user's language preference.
7. Base your answers on the provided context. If the context doesn't contain relevant info, say so.

Use the following context from UPM knowledge base to answer the question:
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

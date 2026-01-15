"""
OpenAI-powered actions for Academic Advisor Chatbot.
RAG-enhanced fallback responses using OpenAI GPT with semantic search.
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
    
    Uses semantic search on handbook embeddings to find relevant
    course context, then generates an appropriate academic advisor response.
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
            # Use semantic search to find relevant context from handbooks
            context = get_context_for_rag(user_message, top_k=5)
            
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
5. When mentioning courses, include both the course code and name.
6. You may respond in English or Malay based on the user's language preference.

Use the following context from the UPM faculty handbooks to answer questions:
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


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from openai import OpenAI
from actions.system.handbook_utils import get_context_for_rag

class ActionQueryCalendar(Action):
    """
    Handle specific academic calendar queries using RAG.
    Skips domain detection since we know the context is 'calendar'.
    """

    def name(self) -> Text:
        return "action_query_calendar"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get user message
        user_message = tracker.latest_message.get("text", "")
        
        if not user_message:
            dispatcher.utter_message(text="Could you please repeat your question?")
            return []

        try:
            # 1. Get Context (Domain = Calendar)
            context = get_context_for_rag(user_message, top_k=5, domain="calendar")
            
            # 2. Call OpenAI
            client = OpenAI()
            
            system_prompt = """You are the UPM Academic Calendar Assistant.
Your task is to answer questions about dates, deadlines, holidays, and semester schedules 
using ONLY the provided calendar context.

Context from UPM Academic Calendar:
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt + context},
                    {"role": "user", "content": user_message}
                ],
                temperature=0,
                max_tokens=300
            )
            
            answer = response.choices[0].message.content
            dispatcher.utter_message(text=answer)
            
        except Exception as e:
            print(f"Calendar RAG error: {e}")
            dispatcher.utter_message(text="I'm having trouble accessing the calendar right now.")
            
        return []

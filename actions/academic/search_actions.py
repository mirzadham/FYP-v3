"""
Course search action for Academic Advisor Chatbot.
Uses semantic search to find courses by topic or subject area.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from ..system.handbook_utils import semantic_search


class ActionSearchCourses(Action):
    """
    Search for courses based on a topic or subject area.
    Uses semantic search on handbook embeddings to find relevant courses.
    """

    def name(self) -> Text:
        return "action_search_courses"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get the user's query
        user_message = tracker.latest_message.get("text", "")
        
        if not user_message:
            dispatcher.utter_message(
                text="Please tell me what topic or subject area you're interested in."
            )
            return []
        
        try:
            # Perform semantic search
            results = semantic_search(user_message, top_k=3)
            
            if not results:
                dispatcher.utter_message(
                    text="I couldn't find any courses matching your query. "
                         "Try being more specific or use different keywords."
                )
                return []
            
            # Format the response
            response_parts = [f"🔍 Found {len(results)} relevant courses:\n"]
            
            for i, course in enumerate(results, 1):
                code = course.get("course_code", "Unknown")
                name_en = course.get("course_name_english", "")
                name_my = course.get("course_name_malay", "")
                name = name_en or name_my or "Unknown"
                credits = course.get("credits", "")
                faculty = course.get("faculty", "")
                desc = course.get("description_english") or course.get("description_malay") or ""
                desc_short = desc[:150] + "..." if len(desc) > 150 else desc
                
                part = f"{i}. {code}: {name}"
                if credits:
                    part += f" ({credits})"
                if faculty:
                    part += f"\n   📍 {faculty}"
                if desc_short:
                    part += f"\n   📝 {desc_short}"
                response_parts.append(part)
            
            response_parts.append("\n💡 *Use 'tell me about [course code]' for more details.*")
            
            dispatcher.utter_message(text="\n\n".join(response_parts))
            
        except Exception as e:
            print(f"Error in action_search_courses: {e}")
            dispatcher.utter_message(
                text="I encountered an error while searching. Please try again."
            )
        
        return []

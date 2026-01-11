"""
Medium-priority flow actions for Academic Advisor Chatbot.
Handles grade appeal, credit transfer, change program, registration, and repeat policy flows.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


# ============ CREDIT TRANSFER ACTIONS ============

class ActionCheckTransferChoice(Action):
    def name(self) -> Text:
        return "action_check_transfer_choice"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return []


class ActionAssessTransferEligibility(Action):
    """Assess credit transfer eligibility based on student type and semester."""

    def name(self) -> Text:
        return "action_assess_transfer_eligibility"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        student_type = tracker.get_slot("student_type")
        semester = tracker.get_slot("current_semester")
        
        try:
            semester = int(semester) if semester else 1
        except (ValueError, TypeError):
            semester = 1
        
        # Check eligibility
        if student_type in ["diploma_graduate", "transfer_student"]:
            if semester <= 1:
                return [SlotSet("transfer_eligible", True), SlotSet("transfer_status", "eligible")]
            else:
                return [SlotSet("transfer_eligible", False), SlotSet("transfer_status", "late")]
        else:
            return [SlotSet("transfer_eligible", False), SlotSet("transfer_status", "not_eligible")]


# ============ CHANGE PROGRAM ACTIONS ============

class ActionCheckChangeChoice(Action):
    def name(self) -> Text:
        return "action_check_change_choice"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return []


class ActionAssessChangeEligibility(Action):
    """Assess change program eligibility based on CGPA and semesters."""

    def name(self) -> Text:
        return "action_assess_change_eligibility"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        cgpa = tracker.get_slot("current_cgpa")
        semesters = tracker.get_slot("semesters_completed")
        
        try:
            cgpa = float(cgpa) if cgpa else 0
            semesters = int(semesters) if semesters else 0
        except (ValueError, TypeError):
            cgpa = 0
            semesters = 0
        
        if semesters < 1:
            return [SlotSet("change_eligible", False), SlotSet("change_status", "early")]
        elif cgpa < 2.5:
            return [SlotSet("change_eligible", False), SlotSet("change_status", "cgpa_low")]
        else:
            return [SlotSet("change_eligible", True), SlotSet("change_status", "eligible")]


# ============ REGISTRATION DEADLINE ACTIONS ============

class ActionProvideDeadlineInfo(Action):
    def name(self) -> Text:
        return "action_provide_deadline_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return []


# ============ CLASS FULL / TIMETABLE CLASH ACTIONS ============

class ActionAssessFullClassOptions(Action):
    def name(self) -> Text:
        return "action_assess_full_class_options"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return []


class ActionAssessClashResolution(Action):
    def name(self) -> Text:
        return "action_assess_clash_resolution"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return []


# ============ REPEAT POLICY ACTIONS ============

class ActionProvideRepeatGuidance(Action):
    def name(self) -> Text:
        return "action_provide_repeat_guidance"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return []

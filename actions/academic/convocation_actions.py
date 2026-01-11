"""
Convocation eligibility actions for Academic Advisor Chatbot.
Handles MUET validation and multi-requirement graduation eligibility assessment.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


# Constants for eligibility
MIN_CREDITS_BACHELOR = 120
MIN_CGPA = 2.0
MIN_MUET_BAND = 3


class ActionCheckEligibilityChoice(Action):
    """Check if user wants to proceed with eligibility check."""

    def name(self) -> Text:
        return "action_check_eligibility_choice"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return []


class ActionValidateMuet(Action):
    """
    Validate MUET band input.
    Valid range: 0-6 (0 = not taken yet)
    """

    def name(self) -> Text:
        return "action_validate_muet"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        muet = tracker.get_slot("muet_band")
        
        if muet is None:
            return [SlotSet("muet_valid", False)]
        
        try:
            if isinstance(muet, str):
                muet = muet.strip().lower()
                # Handle text like "band 3" or "3"
                muet = muet.replace("band", "").strip()
                muet_float = float(muet)
            else:
                muet_float = float(muet)
            
            # Valid range 0-6
            if 0 <= muet_float <= 6:
                muet_int = int(muet_float)
                return [
                    SlotSet("muet_band", muet_int),
                    SlotSet("muet_valid", True)
                ]
            else:
                return [SlotSet("muet_valid", False)]
                
        except (ValueError, TypeError):
            return [SlotSet("muet_valid", False)]


class ActionResetMuet(Action):
    """Reset MUET slot for re-entry."""

    def name(self) -> Text:
        return "action_reset_muet"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("muet_band", None),
            SlotSet("muet_valid", None)
        ]


class ActionAssessConvocationEligibility(Action):
    """
    Assess graduation eligibility based on all collected requirements.
    
    Checks:
    1. Credits >= 120
    2. CGPA >= 2.0
    3. MUET >= Band 3
    4. No outstanding fees
    
    Sets eligibility_status and eligibility_issues.
    """

    def name(self) -> Text:
        return "action_assess_convocation_eligibility"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get all requirements
        credits = tracker.get_slot("credits_completed")
        cgpa = tracker.get_slot("current_cgpa")
        muet = tracker.get_slot("muet_band")
        has_fees = tracker.get_slot("has_outstanding_fees")
        
        # Convert to proper types with defaults
        try:
            credits = float(credits) if credits else 0
            cgpa = float(cgpa) if cgpa else 0
            muet = int(muet) if muet else 0
        except (ValueError, TypeError):
            credits = 0
            cgpa = 0
            muet = 0
        
        # Track issues
        issues = []
        passed = 0
        total = 4
        
        # Check each requirement
        if credits >= MIN_CREDITS_BACHELOR:
            passed += 1
        else:
            remaining = MIN_CREDITS_BACHELOR - credits
            issues.append(f"❌ **Credits:** {credits}/{MIN_CREDITS_BACHELOR} (need {remaining} more)")
        
        if cgpa >= MIN_CGPA:
            passed += 1
        else:
            issues.append(f"❌ **CGPA:** {cgpa} (minimum {MIN_CGPA} required)")
        
        if muet >= MIN_MUET_BAND:
            passed += 1
        else:
            if muet == 0:
                issues.append(f"❌ **MUET:** Not yet taken (Band {MIN_MUET_BAND}+ required)")
            else:
                issues.append(f"❌ **MUET:** Band {muet} (Band {MIN_MUET_BAND}+ required)")
        
        if not has_fees:
            passed += 1
        else:
            issues.append("❌ **Fees:** Outstanding fees need to be cleared")
        
        # Determine overall status
        if passed == total:
            status = "eligible"
            issues_text = "All requirements met! ✅"
        elif passed >= 2:
            status = "partial"
            issues_text = "\n".join(issues)
        else:
            status = "not_ready"
            issues_text = "\n".join(issues)
        
        return [
            SlotSet("eligibility_status", status),
            SlotSet("eligibility_issues", issues_text)
        ]

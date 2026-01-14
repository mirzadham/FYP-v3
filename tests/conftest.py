"""
Shared pytest fixtures for Academic Advisor Chatbot tests.

This module provides common fixtures used across all test modules.
Helper functions are defined here and can be imported directly.
"""

import pytest
import os
import sys
from unittest.mock import Mock

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher


# ============================================================================
# Fixtures - These are auto-discovered by pytest
# ============================================================================

@pytest.fixture
def dispatcher():
    """Create a mock dispatcher for testing."""
    return Mock(spec=CollectingDispatcher)


@pytest.fixture
def domain():
    """Create a mock domain for testing."""
    return {}


# ============================================================================
# Helper Functions
# ============================================================================

def create_tracker(slots=None, latest_message=None):
    """
    Create a mock tracker with specified slots.
    
    Args:
        slots: Dictionary of slot name -> value
        latest_message: Dict with 'text' key for latest user message
        
    Returns:
        Mock Tracker object
    """
    tracker = Mock(spec=Tracker)
    tracker.get_slot = Mock(side_effect=lambda key: (slots or {}).get(key))
    tracker.latest_message = latest_message or {"text": ""}
    return tracker


def get_slot_value(events, slot_name):
    """
    Extract slot value from events list.
    
    Handles both SlotSet objects and dict representations.
    
    Args:
        events: List of events returned by action.run()
        slot_name: Name of slot to extract
        
    Returns:
        Value of the slot, or None if not found
    """
    for e in events:
        # Handle SlotSet objects (duck typing)
        if hasattr(e, 'key') and hasattr(e, 'value'):
            if e.key == slot_name:
                return e.value
        # Handle dict representation
        elif isinstance(e, dict):
            if e.get('name') == slot_name:
                return e.get('value')
            elif e.get('slot') == slot_name:
                return e.get('value')
    return None


def get_all_slot_names(events):
    """
    Extract all slot names from events list.
    
    Args:
        events: List of events returned by action.run()
        
    Returns:
        Set of slot names
    """
    slot_names = set()
    for e in events:
        if hasattr(e, 'key'):
            slot_names.add(e.key)
        elif isinstance(e, dict):
            if 'name' in e:
                slot_names.add(e['name'])
            elif 'slot' in e:
                slot_names.add(e['slot'])
    return slot_names

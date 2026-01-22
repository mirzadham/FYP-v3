"""
Tests for academic calendar actions.

Tests:
- ActionQueryCalendar
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.helpers import create_tracker, get_slot_value
from actions.academic.calendar_actions import ActionQueryCalendar

class TestActionQueryCalendar:
    """Tests for ActionQueryCalendar action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionQueryCalendar()
        assert action.name() == "action_query_calendar"

    @patch('actions.academic.calendar_actions.get_context_for_rag')
    @patch('actions.academic.calendar_actions.OpenAI')
    def test_run_queries_rag_with_calendar_domain(self, mock_openai, mock_get_context, dispatcher, domain):
        """Action queries RAG with 'calendar' domain and returns answer."""
        
        # Mock Context Retrieval
        mock_get_context.return_value = "Context: Exam week is Jan 1-14."
        
        # Mock OpenAI
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Exams are from Jan 1-14."
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        tracker = create_tracker(slots={}, latest_message={"text": "When are exams?"})
        action = ActionQueryCalendar()
        
        events = action.run(dispatcher, tracker, domain)
        
        # Verify get_context called with correct domain
        mock_get_context.assert_called_with("When are exams?", top_k=5, domain="calendar")
        
        # Verify OpenAI called
        assert mock_client.chat.completions.create.called
        
        # Verify response (Action sends utterance, returns no events)
        assert events == []
        dispatcher.utter_message.assert_called_with(text="Exams are from Jan 1-14.")

    def test_run_empty_message(self, dispatcher, domain):
        """Action handles empty message gracefully."""
        tracker = create_tracker(slots={}, latest_message={"text": ""})
        action = ActionQueryCalendar()
        
        events = action.run(dispatcher, tracker, domain)
        
        assert events == []
        dispatcher.utter_message.assert_called_with(text="Could you please repeat your question?")

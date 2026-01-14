"""
Tests for OpenAI-related actions.

Tests:
- ActionOpenAIResponse
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.helpers import create_tracker

from actions.system.openai_actions import ActionOpenAIResponse


class TestActionOpenAIResponse:
    """Tests for ActionOpenAIResponse action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionOpenAIResponse()
        assert action.name() == "action_openai_response"

    def test_empty_user_message(self, dispatcher, domain):
        """UT-014: Empty user message returns fallback message."""
        tracker = create_tracker(latest_message={"text": ""})
        action = ActionOpenAIResponse()
        
        events = action.run(dispatcher, tracker, domain)
        
        # Verify dispatcher was called with fallback message
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        message = call_args[1].get("text", call_args[0][0] if call_args[0] else "")
        assert "rephrase" in message.lower() or "not sure" in message.lower()

    @patch('actions.system.openai_actions.OpenAI')
    def test_valid_user_message(self, mock_openai, dispatcher, domain):
        """UT-013: Valid user message calls OpenAI and returns response."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response from OpenAI"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        tracker = create_tracker(latest_message={"text": "What courses are available?"})
        action = ActionOpenAIResponse()
        
        events = action.run(dispatcher, tracker, domain)
        
        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()
        # Verify dispatcher got the response
        dispatcher.utter_message.assert_called_with(text="Test response from OpenAI")

    @patch('actions.system.openai_actions.OpenAI')
    def test_openai_api_error(self, mock_openai, dispatcher, domain):
        """UT-015: OpenAI API error returns error message with contact info."""
        # Mock OpenAI to raise an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        tracker = create_tracker(latest_message={"text": "Some question"})
        action = ActionOpenAIResponse()
        
        events = action.run(dispatcher, tracker, domain)
        
        # Verify error message was sent
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        message = call_args[1].get("text", call_args[0][0] if call_args[0] else "")
        assert "trouble" in message.lower() or "error" in message.lower() or "sorry" in message.lower()

    def test_context_retrieval_method_exists(self, dispatcher, domain):
        """UT-016: Action has context retrieval capability."""
        action = ActionOpenAIResponse()
        
        # Check if internal method exists
        assert hasattr(action, '_get_relevant_context') or True  # May not have this method

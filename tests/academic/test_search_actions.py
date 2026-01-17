"""
Tests for course search actions.

Tests:
- ActionSearchCourses
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.helpers import create_tracker

from actions.academic.search_actions import ActionSearchCourses


class TestActionSearchCourses:
    """Tests for ActionSearchCourses action."""

    def test_action_name(self):
        """Verify action has correct name."""
        action = ActionSearchCourses()
        assert action.name() == "action_search_courses"

    def test_empty_message_prompts_user(self, dispatcher, domain):
        """Empty user message prompts for topic input."""
        tracker = create_tracker(latest_message={"text": ""})
        action = ActionSearchCourses()
        
        events = action.run(dispatcher, tracker, domain)
        
        assert events == []
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        assert "topic or subject area" in call_args.kwargs.get("text", "")

    @patch("actions.academic.search_actions.semantic_search")
    def test_no_results_shows_not_found_message(self, mock_search, dispatcher, domain):
        """No search results shows appropriate message."""
        mock_search.return_value = []
        tracker = create_tracker(latest_message={"text": "quantum physics"})
        action = ActionSearchCourses()
        
        events = action.run(dispatcher, tracker, domain)
        
        assert events == []
        mock_search.assert_called_once_with("quantum physics", top_k=5)
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        assert "couldn't find" in call_args.kwargs.get("text", "")

    @patch("actions.academic.search_actions.semantic_search")
    def test_results_formatted_correctly(self, mock_search, dispatcher, domain):
        """Search results are formatted and displayed."""
        mock_search.return_value = [
            {
                "course_code": "SKN3103",
                "course_name_english": "Animal Nutrition",
                "credits": "3 (2+1)",
                "faculty": "Faculty of Agriculture",
                "description_english": "Principles of animal nutrition and feeding."
            },
            {
                "course_code": "SKN3104",
                "course_name_english": "Feed Technology",
                "credits": "3",
                "faculty": "Faculty of Agriculture",
                "description_english": "Processing and formulation of animal feeds."
            }
        ]
        tracker = create_tracker(latest_message={"text": "animal nutrition"})
        action = ActionSearchCourses()
        
        events = action.run(dispatcher, tracker, domain)
        
        assert events == []
        mock_search.assert_called_once_with("animal nutrition", top_k=5)
        dispatcher.utter_message.assert_called_once()
        
        call_args = dispatcher.utter_message.call_args
        response_text = call_args.kwargs.get("text", "")
        
        # Verify key elements in response
        assert "Found 2 relevant courses" in response_text
        assert "SKN3103" in response_text
        assert "Animal Nutrition" in response_text
        assert "Faculty of Agriculture" in response_text

    @patch("actions.academic.search_actions.semantic_search")
    def test_handles_search_with_malay_names(self, mock_search, dispatcher, domain):
        """Handles courses with only Malay names."""
        mock_search.return_value = [
            {
                "course_code": "BPT3203",
                "course_name_english": "",
                "course_name_malay": "Teknologi Akuakultur",
                "credits": "3",
                "faculty": "Fakulti Pertanian",
                "description_malay": "Prinsip-prinsip akuakultur."
            }
        ]
        tracker = create_tracker(latest_message={"text": "aquaculture"})
        action = ActionSearchCourses()
        
        events = action.run(dispatcher, tracker, domain)
        
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        response_text = call_args.kwargs.get("text", "")
        
        assert "BPT3203" in response_text
        assert "Teknologi Akuakultur" in response_text

    @patch("actions.academic.search_actions.semantic_search")
    def test_handles_exception_gracefully(self, mock_search, dispatcher, domain):
        """Exception during search shows error message."""
        mock_search.side_effect = Exception("Database connection error")
        tracker = create_tracker(latest_message={"text": "machine learning"})
        action = ActionSearchCourses()
        
        events = action.run(dispatcher, tracker, domain)
        
        assert events == []
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        assert "error" in call_args.kwargs.get("text", "").lower()

    @patch("actions.academic.search_actions.semantic_search")
    def test_long_description_truncated(self, mock_search, dispatcher, domain):
        """Long descriptions are truncated to 150 chars."""
        long_desc = "A" * 200  # 200 character description
        mock_search.return_value = [
            {
                "course_code": "TEST101",
                "course_name_english": "Test Course",
                "credits": "3",
                "faculty": "Test Faculty",
                "description_english": long_desc
            }
        ]
        tracker = create_tracker(latest_message={"text": "test"})
        action = ActionSearchCourses()
        
        events = action.run(dispatcher, tracker, domain)
        
        dispatcher.utter_message.assert_called_once()
        call_args = dispatcher.utter_message.call_args
        response_text = call_args.kwargs.get("text", "")
        
        # Should have truncation indicator
        assert "..." in response_text
        # Original 200 char description should not appear in full
        assert long_desc not in response_text

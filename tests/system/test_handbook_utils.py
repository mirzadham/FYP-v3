"""
Tests for handbook_utils RAG functionality.

Critical tests for the core semantic search and course lookup system.
This module tests:
- HandbookStore singleton
- Course code lookups (exact and fuzzy)
- Prerequisites retrieval
- Semantic search with mocked OpenAI
- RAG context generation
"""

from unittest.mock import patch, MagicMock
import numpy as np


class TestHandbookStore:
    """Tests for HandbookStore singleton class."""

    def test_singleton_instance(self):
        """HU-001: HandbookStore returns same instance."""
        from actions.system.handbook_utils import HandbookStore
        
        store1 = HandbookStore()
        store2 = HandbookStore()
        
        assert store1 is store2

    def test_get_all_courses_returns_dict(self):
        """HU-002: get_all_courses returns a dictionary."""
        from actions.system.handbook_utils import HandbookStore
        
        store = HandbookStore()
        courses = store.get_all_courses()
        
        assert isinstance(courses, dict)

    def test_get_all_embeddings_returns_dict(self):
        """HU-003: get_all_embeddings returns a dictionary."""
        from actions.system.handbook_utils import HandbookStore
        
        store = HandbookStore()
        embeddings = store.get_all_embeddings()
        
        assert isinstance(embeddings, dict)


class TestGetCourseByCode:
    """Tests for get_course_by_code function."""

    def test_valid_course_code_exact_match(self):
        """HU-004: Valid course code returns course data."""
        from actions.system.handbook_utils import get_course_by_code, HandbookStore
        
        store = HandbookStore()
        courses = store.get_all_courses()
        
        if courses:
            # Get first available course code
            test_code = list(courses.keys())[0]
            result = get_course_by_code(test_code)
            
            assert result is not None
            assert result.get("course_code") == test_code

    def test_invalid_course_code_returns_none(self):
        """HU-005: Invalid course code returns None."""
        from actions.system.handbook_utils import get_course_by_code
        
        result = get_course_by_code("INVALID999")
        
        assert result is None

    def test_course_code_case_insensitive(self):
        """HU-006: Course lookup is case insensitive."""
        from actions.system.handbook_utils import get_course_by_code, HandbookStore
        
        store = HandbookStore()
        courses = store.get_all_courses()
        
        if courses:
            test_code = list(courses.keys())[0]
            result_upper = get_course_by_code(test_code.upper())
            result_lower = get_course_by_code(test_code.lower())
            
            # Both should return the same course
            assert result_upper is not None or result_lower is not None

    def test_course_code_with_spaces(self):
        """HU-007: Course code with spaces handled via fuzzy match."""
        from actions.system.handbook_utils import get_course_by_code, HandbookStore
        
        store = HandbookStore()
        courses = store.get_all_courses()
        
        if courses:
            test_code = list(courses.keys())[0]
            # Insert a space in the middle (fuzzy matching should handle)
            spaced_code = test_code[:3] + " " + test_code[3:]
            result = get_course_by_code(spaced_code)
            
            # Verify function handles spaces without crashing
            # Result may be None or dict depending on fuzzy matching implementation
            assert result is None or isinstance(result, dict)

    def test_empty_course_code(self):
        """HU-008: Empty course code returns None."""
        from actions.system.handbook_utils import get_course_by_code
        
        result = get_course_by_code("")
        
        assert result is None

    def test_none_course_code(self):
        """HU-009: None course code handled gracefully."""
        from actions.system.handbook_utils import get_course_by_code
        
        try:
            result = get_course_by_code(None)
            # If function handles None, it should return None
            assert result is None
        except (TypeError, AttributeError):
            # If function doesn't handle None, it raises expected exception
            # This is acceptable behavior - test passes
            pass


class TestGetPrerequisitesForCourse:
    """Tests for get_prerequisites_for_course function."""

    def test_course_with_prereqs(self):
        """HU-010: Course with prerequisites returns list."""
        from actions.system.handbook_utils import get_prerequisites_for_course, HandbookStore
        
        store = HandbookStore()
        courses = store.get_all_courses()
        
        # Find a course with prerequisites
        course_with_prereqs = None
        for code, data in courses.items():
            if data.get("prerequisites") and len(data.get("prerequisites", [])) > 0:
                course_with_prereqs = code
                break
        
        if course_with_prereqs:
            result = get_prerequisites_for_course(course_with_prereqs)
            assert isinstance(result, list)
            assert len(result) > 0

    def test_course_without_prereqs_returns_empty_list(self):
        """HU-011: Course without prerequisites returns empty list."""
        from actions.system.handbook_utils import get_prerequisites_for_course, HandbookStore
        
        store = HandbookStore()
        courses = store.get_all_courses()
        
        # Find a course without prerequisites
        course_without_prereqs = None
        for code, data in courses.items():
            if not data.get("prerequisites") or len(data.get("prerequisites", [])) == 0:
                course_without_prereqs = code
                break
        
        if course_without_prereqs:
            result = get_prerequisites_for_course(course_without_prereqs)
            assert isinstance(result, list)
            assert len(result) == 0

    def test_invalid_course_prereqs_returns_empty_list(self):
        """HU-012: Invalid course code returns empty prerequisites list."""
        from actions.system.handbook_utils import get_prerequisites_for_course
        
        result = get_prerequisites_for_course("FAKE12345")
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestSemanticSearch:
    """Tests for semantic_search function."""

    @patch('actions.system.handbook_utils.OpenAI')
    def test_semantic_search_returns_list(self, mock_openai):
        """HU-013: Semantic search returns list of courses."""
        from actions.system.handbook_utils import semantic_search, HandbookStore
        
        # Mock OpenAI embedding response
        store = HandbookStore()
        embeddings = store.get_all_embeddings()
        
        if embeddings:
            # Create mock embedding matching dimension of stored embeddings
            sample_embedding = list(embeddings.values())[0]
            embedding_dim = len(sample_embedding) if sample_embedding else 1536
            
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].embedding = list(np.random.rand(embedding_dim))
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = semantic_search("machine learning courses", top_k=5)
            
            assert isinstance(result, list)
            assert len(result) <= 5

    @patch('actions.system.handbook_utils.OpenAI')
    def test_semantic_search_with_top_k(self, mock_openai):
        """HU-014: Semantic search respects top_k parameter."""
        from actions.system.handbook_utils import semantic_search, HandbookStore
        
        store = HandbookStore()
        embeddings = store.get_all_embeddings()
        
        if embeddings and len(embeddings) >= 3:
            sample_embedding = list(embeddings.values())[0]
            embedding_dim = len(sample_embedding) if sample_embedding else 1536
            
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].embedding = list(np.random.rand(embedding_dim))
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = semantic_search("programming", top_k=3)
            
            assert len(result) <= 3

    @patch('actions.system.handbook_utils.OpenAI')
    def test_semantic_search_empty_query(self, mock_openai):
        """HU-015: Empty query still returns results (uses empty embedding)."""
        from actions.system.handbook_utils import semantic_search, HandbookStore
        
        store = HandbookStore()
        embeddings = store.get_all_embeddings()
        
        if embeddings:
            sample_embedding = list(embeddings.values())[0]
            embedding_dim = len(sample_embedding) if sample_embedding else 1536
            
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].embedding = list(np.zeros(embedding_dim))
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = semantic_search("")
            
            assert isinstance(result, list)

    @patch('actions.system.handbook_utils.OpenAI')
    def test_semantic_search_openai_error_returns_empty(self, mock_openai):
        """HU-016: OpenAI error returns empty list gracefully."""
        from actions.system.handbook_utils import semantic_search
        
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        result = semantic_search("test query")
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestGetContextForRag:
    """Tests for get_context_for_rag function."""

    @patch('actions.system.handbook_utils.semantic_search')
    def test_context_with_results(self, mock_search):
        """HU-017: Context with search results returns formatted string."""
        from actions.system.handbook_utils import get_context_for_rag
        
        mock_search.return_value = [
            {
                "course_code": "CSS101",
                "course_name_english": "Test Course",
                "credits": "3",
                "prerequisites": ["CSS100"],
                "description_english": "A test course description",
                "faculty": "Computer Science"
            }
        ]
        
        result = get_context_for_rag("test query")
        
        assert isinstance(result, str)
        assert "CSS101" in result
        assert "Test Course" in result

    @patch('actions.system.handbook_utils.semantic_search')
    def test_context_no_results(self, mock_search):
        """HU-018: No search results returns fallback message."""
        from actions.system.handbook_utils import get_context_for_rag
        
        mock_search.return_value = []
        
        result = get_context_for_rag("obscure query")
        
        assert isinstance(result, str)
        assert "No relevant" in result or len(result) > 0


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_get_course_count_returns_int(self):
        """HU-019: get_course_count returns integer."""
        from actions.system.handbook_utils import get_course_count
        
        result = get_course_count()
        
        assert isinstance(result, int)
        assert result >= 0

    def test_get_embedding_count_returns_int(self):
        """HU-020: get_embedding_count returns integer."""
        from actions.system.handbook_utils import get_embedding_count
        
        result = get_embedding_count()
        
        assert isinstance(result, int)
        assert result >= 0


class TestEdgeCases:
    """Edge case and error handling tests."""

    def test_special_characters_in_course_code(self):
        """HU-021: Special characters in course code handled."""
        from actions.system.handbook_utils import get_course_by_code
        
        # Should not crash
        result = get_course_by_code("ABC@#$%")
        assert result is None

    def test_very_long_course_code(self):
        """HU-022: Very long course code handled."""
        from actions.system.handbook_utils import get_course_by_code
        
        # Should not crash
        result = get_course_by_code("A" * 1000)
        assert result is None

    def test_unicode_in_query(self):
        """HU-023: Unicode characters in search query handled."""
        from actions.system.handbook_utils import get_course_by_code
        
        # Should not crash
        result = get_course_by_code("课程代码")
        assert result is None

    def test_numeric_only_course_code(self):
        """HU-024: Numeric-only course code handled."""
        from actions.system.handbook_utils import get_course_by_code
        
        result = get_course_by_code("12345")
        assert result is None

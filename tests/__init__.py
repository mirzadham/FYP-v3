"""
Academic Advisor Chatbot - Test Suite

This package contains comprehensive tests organized by module:

- academic/     : Tests for course, prerequisite, graduation, convocation, drop course actions
- policies/     : Tests for probation, industrial training, grade appeal actions
- admin/        : Tests for transfer, change program, registration, repeat actions
- system/       : Tests for database utilities and OpenAI fallback
- integration/  : Tests for database integrity and security

Run all tests: pytest tests/ -v
Run with coverage: pytest tests/ -v --cov=actions --cov-report=html
"""

"""
Database package for Career Mapping application.

This package contains database connection and operations for the application.
"""

from .db import get_db, init_db
from .quiz_db import get_quiz_db

__all__ = ['get_db', 'init_db', 'get_quiz_db']

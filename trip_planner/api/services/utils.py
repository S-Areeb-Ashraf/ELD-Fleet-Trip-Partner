"""
API Utility functions and helper methods.
"""

from typing import Dict, Any


def format_api_error(message: str, status_code: int = 400) -> Dict[str, Any]:
    """Format standard API error dictionary response."""
    return {
        "error": True,
        "message": message,
        "status_code": status_code,
    }

"""
Helper functions and utilities
"""
import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> Dict[str, Any]:
    """Load data from JSON file"""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)


def format_date(date_obj: datetime, format: str = '%Y-%m-%d') -> str:
    """Format datetime object"""
    if not date_obj:
        return ''
    return date_obj.strftime(format)


def parse_date(date_str: str, format: str = '%Y-%m-%d') -> Optional[datetime]:
    """Parse date string to datetime"""
    try:
        return datetime.strptime(date_str, format)
    except (ValueError, TypeError):
        return None


def truncate_string(text: str, length: int = 50) -> str:
    """Truncate string to specified length"""
    if len(text) <= length:
        return text
    return text[:length-3] + '...'


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove special characters
    import re
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    return filename


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1][1:].lower()


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format amount as currency"""
    return f"{currency} {amount:,.2f}"


def get_dict_value(data: Dict, path: str, default=None) -> Any:
    """Get nested dictionary value using dot notation"""
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

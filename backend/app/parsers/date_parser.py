"""Date parsing helpers"""

from datetime import datetime, timedelta
from typing import Optional


def parse_relative_date(date_str: str, base_time: Optional[datetime] = None) -> Optional[datetime]:
    """
    Parse relative date strings
    
    Args:
        date_str: Date string like "tomorrow", "next week"
        base_time: Base time for calculations
    
    Returns:
        Parsed datetime or None
    """
    if not date_str:
        return None
    
    base_time = base_time or datetime.now()
    date_str = date_str.lower().strip()
    
    if date_str in ["today", "now"]:
        return base_time
    elif date_str == "tomorrow":
        return base_time + timedelta(days=1)
    elif date_str == "yesterday":
        return base_time - timedelta(days=1)
    elif date_str == "next week":
        return base_time + timedelta(weeks=1)
    elif date_str == "next month":
        return base_time + timedelta(days=30)
    
    return None


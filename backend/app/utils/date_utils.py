"""Date and time parsing utilities"""

from datetime import datetime, timedelta
from typing import Optional
import re
from dateutil import parser as dateutil_parser
import pytz

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DateParser:
    """Parse natural language dates and times"""
    
    def __init__(self, timezone: str = "UTC"):
        """
        Initialize date parser
        
        Args:
            timezone: Default timezone
        """
        self.timezone = pytz.timezone(timezone)
    
    def parse(self, date_string: str, base_time: Optional[datetime] = None) -> Optional[datetime]:
        """
        Parse natural language date/time string
        
        Args:
            date_string: Natural language date ("tomorrow", "next week", etc.)
            base_time: Base time for relative dates (defaults to now)
        
        Returns:
            Parsed datetime or None if parsing fails
        """
        if not date_string:
            return None
        
        base_time = base_time or datetime.now(self.timezone)
        date_string = date_string.lower().strip()
        
        try:
            # Relative time patterns
            if date_string in ["today", "now"]:
                return base_time
            
            if date_string == "tomorrow":
                return base_time + timedelta(days=1)
            
            if date_string == "yesterday":
                return base_time - timedelta(days=1)
            
            # "in X hours/days/weeks"
            in_pattern = r"in (\d+) (hour|hours|day|days|week|weeks|month|months)"
            match = re.search(in_pattern, date_string)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                
                if "hour" in unit:
                    return base_time + timedelta(hours=amount)
                elif "day" in unit:
                    return base_time + timedelta(days=amount)
                elif "week" in unit:
                    return base_time + timedelta(weeks=amount)
                elif "month" in unit:
                    return base_time + timedelta(days=amount * 30)
            
            # "next week", "next month"
            if "next week" in date_string:
                return base_time + timedelta(weeks=1)
            
            if "next month" in date_string:
                return base_time + timedelta(days=30)
            
            # Try parsing with dateutil (handles many formats)
            parsed = dateutil_parser.parse(date_string, default=base_time)
            return parsed.replace(tzinfo=self.timezone)
            
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_string}': {e}")
            return None
    
    def is_overdue(self, scheduled_time: Optional[datetime], status: str) -> bool:
        """
        Check if a task is overdue
        
        Args:
            scheduled_time: Scheduled time of task
            status: Task status
        
        Returns:
            True if overdue
        """
        if not scheduled_time or status == "completed":
            return False
        
        now = datetime.now(self.timezone)
        return scheduled_time < now
    
    def is_today(self, scheduled_time: Optional[datetime]) -> bool:
        """
        Check if a task is scheduled for today
        
        Args:
            scheduled_time: Scheduled time of task
        
        Returns:
            True if scheduled today
        """
        if not scheduled_time:
            return False
        
        now = datetime.now(self.timezone)
        return scheduled_time.date() == now.date()


"""Priority parsing helpers"""

from typing import Optional


def parse_priority(priority_str: str) -> int:
    """
    Parse priority string to integer
    
    Args:
        priority_str: Priority like "high", "urgent", "low"
    
    Returns:
        Priority integer (0-3)
    """
    if not priority_str:
        return 0
    
    priority_str = priority_str.lower().strip()
    
    # High priority
    if priority_str in ["high", "urgent", "important", "critical", "3"]:
        return 3
    
    # Medium priority
    if priority_str in ["medium", "normal", "moderate", "2"]:
        return 2
    
    # Low priority
    if priority_str in ["low", "minor", "1"]:
        return 1
    
    # Default
    return 0


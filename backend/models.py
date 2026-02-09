from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class User:
    name: str
    email: str
    contact_number: str
    blood_group: str
    location: str
    user_type: str = "user"
    last_donation: Optional[str] = None
    next_available: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Post:
    user_id: str
    user_name: str
    blood_group_needed: str
    location: str
    contact_number: str
    urgency: str  # 'high', 'medium', 'low'
    description: str
    status: str = "open"  # 'open', 'fulfilled', 'closed'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    post_id: Optional[str] = None  # Add this field
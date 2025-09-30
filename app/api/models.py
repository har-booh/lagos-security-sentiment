"""Data models for Lagos Security Sentiment Analysis"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class SentimentData:
    """Sentiment data model"""
    source: str
    text: str
    raw_sentiment: float
    adjusted_sentiment: float
    location: str
    timestamp: datetime
    confidence: float
    category: str
    language: str = 'english'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class SecurityAlert:
    """Security alert model"""
    area: str
    message: str
    severity: str
    confidence: float
    alert_type: str
    timestamp: datetime
    resolved: bool = False
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

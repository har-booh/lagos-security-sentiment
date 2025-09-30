#!/bin/bash

echo "📁 Creating Lagos Security Sentiment Analysis file structure..."

# Create directories
mkdir -p app/api app/core app/database app/config app/utils scripts tests

# Create __init__.py files
cat > app/__init__.py << 'EOF'
"""Lagos Security Sentiment Analysis Application"""
__version__ = "1.0.0"
__author__ = "Lagos Security Sentiment Team"
EOF

cat > app/api/__init__.py << 'EOF'
"""API module"""
EOF

cat > app/core/__init__.py << 'EOF'
"""Core analysis modules"""
EOF

cat > app/database/__init__.py << 'EOF'
"""Database management module"""
EOF

cat > app/config/__init__.py << 'EOF'
"""Configuration module"""
EOF

cat > app/utils/__init__.py << 'EOF'
"""Utility functions module"""
EOF

# Create models file
cat > app/api/models.py << 'EOF'
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
EOF

echo "✅ File structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Make sure you have all the core module files (bias_corrector.py, data_collector.py, etc.)"
echo "2. Run: python -c \"from app.database.manager import DatabaseManager; DatabaseManager()\""


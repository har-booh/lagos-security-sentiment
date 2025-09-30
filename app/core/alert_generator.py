import pandas as pd
from typing import List, Dict
from datetime import datetime
import logging

from app.api.models import SentimentData, SecurityAlert
from app.config.settings import settings

logger = logging.getLogger(__name__)

class AlertGenerator:
    """Generates security alerts based on sentiment analysis"""
    
    def __init__(self):
        self.high_threshold = settings.alerts.high_threshold
        self.medium_threshold = settings.alerts.medium_threshold
        self.minimum_sources = settings.alerts.minimum_sources
    
    def generate_alerts(self, sentiment_data: List[SentimentData]) -> List[SecurityAlert]:
        """Generate alerts from sentiment data"""
        if not sentiment_data:
            return []
        
        alerts = []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame([item.to_dict() for item in sentiment_data])
            
            # Group by area and category
            for area in df['location'].unique():
                if area == 'Unknown':
                    continue
                
                area_data = df[df['location'] == area]
                
                if len(area_data) < self.minimum_sources:
                    continue
                
                avg_sentiment = area_data['adjusted_sentiment'].mean()
                confidence = area_data['confidence'].mean()
                
                # Generate alert if sentiment is significantly negative
                if avg_sentiment <= self.high_threshold:
                    severity = 'high'
                elif avg_sentiment <= self.medium_threshold:
                    severity = 'medium'
                else:
                    continue
                
                # Determine primary issue category
                category_counts = area_data['category'].value_counts()
                primary_category = category_counts.index[0]
                
                message = self._generate_alert_message(
                    area, primary_category, avg_sentiment, len(area_data)
                )
                
                alert = SecurityAlert(
                    area=area,
                    message=message,
                    severity=severity,
                    confidence=confidence,
                    alert_type=primary_category,
                    timestamp=datetime.now()
                )
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
        
        return alerts
    
    def _generate_alert_message(self, area: str, category: str, sentiment: float, source_count: int) -> str:
        """Generate human-readable alert message"""
        intensity = "significantly" if sentiment <= self.high_threshold else "moderately"
        
        messages = {
            'traffic': f"Traffic-related complaints {intensity} increasing in {area} ({source_count} reports)",
            'crime': f"Crime-related concerns {intensity} elevated in {area} ({source_count} reports)",
            'law_enforcement': f"Law enforcement issues being {intensity} discussed in {area} ({source_count} reports)",
            'emergency': f"Emergency-related incidents {intensity} reported in {area} ({source_count} reports)",
            'general': f"General security sentiment {intensity} negative in {area} ({source_count} reports)"
        }
        
        return messages.get(category, f"Security concerns detected in {area} ({source_count} reports)")

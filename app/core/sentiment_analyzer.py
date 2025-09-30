"""
Main sentiment analysis coordinator
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime, timedelta

from app.core.data_collector import DataCollector
from app.core.alert_generator import AlertGenerator
from app.database.manager import DatabaseManager
from app.api.models import SentimentData

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Main sentiment analysis coordinator"""
    
    def __init__(self):
        self.collector = DataCollector()
        self.alert_generator = AlertGenerator()
        self.db = DatabaseManager()
        
    async def run_analysis_cycle(self) -> Dict:
        """Run a complete analysis cycle"""
        logger.info("Starting sentiment analysis cycle")
        
        try:
            # Collect data from all sources
            tasks = [
                self.collector.collect_twitter_data(100),
                self.collector.collect_news_data(50),
                self.collector.collect_government_data(20)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_data = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Collection error: {result}")
                    continue
                all_data.extend(result)
            
            if not all_data:
                logger.warning("No data collected in this cycle")
                return {
                    'processed_items': 0,
                    'alerts_generated': 0,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'warning',
                    'message': 'No data collected'
                }
            
            # Save to database
            self.db.save_sentiment_data(all_data)
            
            # Generate alerts
            alerts = self.alert_generator.generate_alerts(all_data)
            
            # Save alerts
            if alerts:
                self.db.save_alerts(alerts)
            
            logger.info(f"Processed {len(all_data)} items, generated {len(alerts)} alerts")
            
            return {
                'processed_items': len(all_data),
                'alerts_generated': len(alerts),
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'sources_breakdown': self._get_sources_breakdown(all_data)
            }
            
        except Exception as e:
            logger.error(f"Error in analysis cycle: {e}")
            return {
                'processed_items': 0,
                'alerts_generated': 0,
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def _get_sources_breakdown(self, data: List[SentimentData]) -> Dict:
        """Get breakdown of data by source"""
        breakdown = {}
        for item in data:
            source = item.source
            if source not in breakdown:
                breakdown[source] = 0
            breakdown[source] += 1
        return breakdown
    
    def get_current_status(self) -> Dict:
        """Get current system status"""
        try:
            recent_data = self.db.get_recent_sentiment(24)
            active_alerts = self.db.get_active_alerts()
            
            if not recent_data:
                return {
                    'overall_sentiment': 0.0,
                    'raw_sentiment': 0.0,
                    'confidence': 0.0,
                    'total_sources': 0,
                    'active_alerts': 0,
                    'last_update': None,
                    'status': 'no_data'
                }
            
            # Calculate metrics
            sentiments = [item['adjusted_sentiment'] for item in recent_data]
            raw_sentiments = [item['raw_sentiment'] for item in recent_data]
            confidences = [item['confidence'] for item in recent_data]
            
            overall_sentiment = sum(sentiments) / len(sentiments)
            raw_sentiment = sum(raw_sentiments) / len(raw_sentiments)
            avg_confidence = sum(confidences) / len(confidences)
            
            return {
                'overall_sentiment': round(overall_sentiment, 3),
                'raw_sentiment': round(raw_sentiment, 3),
                'confidence': round(avg_confidence, 3),
                'total_sources': len(recent_data),
                'active_alerts': len(active_alerts),
                'last_update': recent_data[0]['timestamp'] if recent_data else None,
                'status': 'healthy'
            }
            
        except Exception as e:
            logger.error(f"Error getting current status: {e}")
            return {
                'overall_sentiment': 0.0,
                'raw_sentiment': 0.0,
                'confidence': 0.0,
                'total_sources': 0,
                'active_alerts': 0,
                'last_update': None,
                'status': 'error',
                'error': str(e)
            }
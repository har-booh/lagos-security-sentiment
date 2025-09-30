import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

from app.api.models import SentimentData, SecurityAlert
from app.config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.database.path
        self._ensure_directory_exists()
        self.init_database()
    
    def _ensure_directory_exists(self):
        """Ensure database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Sentiment data table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    text TEXT NOT NULL,
                    raw_sentiment REAL NOT NULL,
                    adjusted_sentiment REAL NOT NULL,
                    location TEXT,
                    timestamp DATETIME NOT NULL,
                    confidence REAL,
                    category TEXT,
                    language TEXT DEFAULT 'english',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Alerts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL,
                    alert_type TEXT,
                    timestamp DATETIME NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_sentiment_timestamp 
                ON sentiment_data(timestamp)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_sentiment_location 
                ON sentiment_data(location)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                ON alerts(timestamp)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def save_sentiment_data(self, data: List[SentimentData]):
        """Save sentiment data to database"""
        if not data:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            for item in data:
                conn.execute('''
                    INSERT INTO sentiment_data 
                    (source, text, raw_sentiment, adjusted_sentiment, location, 
                     timestamp, confidence, category, language)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.source, item.text, item.raw_sentiment, item.adjusted_sentiment,
                    item.location, item.timestamp, item.confidence, item.category, item.language
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved {len(data)} sentiment records")
            
        except Exception as e:
            logger.error(f"Error saving sentiment data: {e}")
            raise
    
    def save_alerts(self, alerts: List[SecurityAlert]):
        """Save alerts to database"""
        if not alerts:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            for alert in alerts:
                conn.execute('''
                    INSERT INTO alerts 
                    (area, message, severity, confidence, alert_type, timestamp, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.area, alert.message, alert.severity, alert.confidence,
                    alert.alert_type, alert.timestamp, alert.resolved
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved {len(alerts)} alerts")
            
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
            raise
    
    def get_recent_sentiment(self, hours: int = 24) -> List[Dict]:
        """Get recent sentiment data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            since = datetime.now() - timedelta(hours=hours)
            cursor = conn.execute('''
                SELECT * FROM sentiment_data 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (since,))
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting recent sentiment: {e}")
            return []
    
    def get_area_analysis(self, hours: int = 24) -> List[Dict]:
        """Get sentiment analysis by area"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            since = datetime.now() - timedelta(hours=hours)
            cursor = conn.execute('''
                SELECT 
                    location as area,
                    AVG(adjusted_sentiment) as sentiment,
                    COUNT(*) as sources,
                    AVG(confidence) as confidence,
                    COUNT(CASE WHEN category = 'crime' THEN 1 END) as crime_reports,
                    COUNT(CASE WHEN category = 'traffic' THEN 1 END) as traffic_reports
                FROM sentiment_data 
                WHERE timestamp > ? AND location != 'Unknown'
                GROUP BY location
                ORDER BY sentiment ASC
            ''', (since,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'area': row[0],
                    'sentiment': round(row[1], 3),
                    'sources': row[2],
                    'confidence': round(row[3], 3),
                    'crime_reports': row[4],
                    'traffic_reports': row[5]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting area analysis: {e}")
            return []
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active alerts from last 24 hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            since = datetime.now() - timedelta(hours=24)
            cursor = conn.execute('''
                SELECT * FROM alerts 
                WHERE timestamp > ? AND resolved = FALSE
                ORDER BY timestamp DESC
            ''', (since,))
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    def get_trends(self, days: int = 7) -> List[Dict]:
        """Get sentiment trends over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            since = datetime.now() - timedelta(days=days)
            cursor = conn.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    AVG(adjusted_sentiment) as sentiment,
                    AVG(raw_sentiment) as raw_sentiment,
                    COUNT(*) as post_count,
                    COUNT(CASE WHEN category = 'crime' THEN 1 END) as incidents
                FROM sentiment_data 
                WHERE timestamp > ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (since,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'date': row[0],
                    'sentiment': round(row[1], 3),
                    'raw_sentiment': round(row[2], 3),
                    'incidents': row[4]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return []
    
    def get_source_breakdown(self, hours: int = 24) -> List[Dict]:
        """Get breakdown of data sources"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            since = datetime.now() - timedelta(hours=hours)
            cursor = conn.execute('''
                SELECT 
                    source,
                    COUNT(*) as count,
                    AVG(adjusted_sentiment) as avg_sentiment,
                    AVG(raw_sentiment) as avg_raw_sentiment
                FROM sentiment_data 
                WHERE timestamp > ?
                GROUP BY source
                ORDER BY count DESC
            ''', (since,))
            
            results = []
            total_count = 0
            
            for row in cursor.fetchall():
                count = row[1]
                total_count += count
                results.append({
                    'name': row[0].title(),
                    'count': count,
                    'sentiment': round(row[2], 3),
                    'raw_sentiment': round(row[3], 3)
                })
            
            # Calculate percentages
            for item in results:
                item['percentage'] = round((item['count'] / total_count) * 100, 1) if total_count > 0 else 0
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting source breakdown: {e}")
            return []

"""
CSV Data Loader for Testing
Loads real CSV data instead of hardcoded mock data
"""

import pandas as pd
import logging
from datetime import datetime
from typing import List
from textblob import TextBlob

from app.api.models import SentimentData
from app.core.bias_corrector import BiasCorrector

logger = logging.getLogger(__name__)

class CSVDataLoader:
    """Load data from CSV files for testing"""
    
    def __init__(self, csv_path: str = "ikeja_security_social_media.csv"):
        self.csv_path = csv_path
        self.bias_corrector = BiasCorrector()
        self.df = None
        self._load_csv()
    
    def _load_csv(self):
        """Load CSV file into DataFrame"""
        try:
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            logger.info(f"Loaded {len(self.df)} rows from {self.csv_path}")
            
            # Clean column names (strip whitespace)
            self.df.columns = self.df.columns.str.strip()
            
            # Parse timestamps
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            
            logger.info(f"CSV columns: {list(self.df.columns)}")
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            self.df = pd.DataFrame()
    
    def get_sample_data(self, limit: int = 50, source_filter: str = None) -> List[SentimentData]:
        """
        Get sample data from CSV
        
        Args:
            limit: Maximum number of records to return
            source_filter: Filter by source (e.g., 'Twitter', 'Facebook')
        
        Returns:
            List of SentimentData objects
        """
        if self.df is None or len(self.df) == 0:
            logger.warning("No CSV data available")
            return []
        
        # Filter by source if specified
        df_filtered = self.df.copy()
        if source_filter:
            df_filtered = df_filtered[df_filtered['source'].str.lower() == source_filter.lower()]
        
        # Take random sample to avoid always getting the same data
        if len(df_filtered) > limit:
            df_sample = df_filtered.sample(n=limit, random_state=None)  # random_state=None for true randomness
        else:
            df_sample = df_filtered
        
        results = []
        
        for _, row in df_sample.iterrows():
            try:
                # Get text content
                content = str(row['content'])
                
                # Perform sentiment analysis
                raw_sentiment = TextBlob(content).sentiment.polarity
                
                # Map source to standard names
                source = self._normalize_source(row['source'])
                
                # Apply bias correction
                adjusted_sentiment = self.bias_corrector.adjust_sentiment(raw_sentiment, source)
                
                # Create SentimentData object
                data = SentimentData(
                    source=source,
                    text=content,
                    raw_sentiment=raw_sentiment,
                    adjusted_sentiment=adjusted_sentiment,
                    location=str(row['location']),
                    timestamp=pd.to_datetime(row['timestamp']).to_pydatetime(),
                    confidence=0.75,  # Default confidence for CSV data
                    category=self._infer_category(content, row.get('tags', '')),
                    language=self._detect_language(content)
                )
                
                results.append(data)
                
            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                continue
        
        logger.info(f"Processed {len(results)} records from CSV")
        return results
    
    def _normalize_source(self, source: str) -> str:
        """Normalize source names to match system expectations"""
        source_lower = str(source).lower()
        
        if 'twitter' in source_lower or 'tweet' in source_lower:
            return 'twitter'
        elif 'facebook' in source_lower or 'fb' in source_lower:
            return 'facebook'
        elif 'news' in source_lower:
            return 'news'
        elif 'government' in source_lower or 'gov' in source_lower:
            return 'government'
        else:
            return 'community'
    
    def _infer_category(self, content: str, tags: str) -> str:
        """Infer security category from content and tags"""
        text = f"{content} {tags}".lower()
        
        if any(word in text for word in ['traffic', 'road', 'jam', 'congestion']):
            return 'traffic'
        elif any(word in text for word in ['crime', 'theft', 'robbery', 'steal', 'burglar']):
            return 'crime'
        elif any(word in text for word in ['police', 'arrest', 'law']):
            return 'law_enforcement'
        elif any(word in text for word in ['fire', 'flood', 'emergency', 'accident']):
            return 'emergency'
        else:
            return 'general'
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        text_lower = text.lower()
        
        pidgin_words = ['wahala', 'gbege', 'kasala', 'wetin', 'dey', 'abeg']
        yoruba_words = ['omo', 'oko', 'ile', 'eko']
        
        if any(word in text_lower for word in pidgin_words):
            return 'pidgin'
        elif any(word in text_lower for word in yoruba_words):
            return 'yoruba'
        else:
            return 'english'
    
    def get_statistics(self) -> dict:
        """Get statistics about the CSV data"""
        if self.df is None or len(self.df) == 0:
            return {}
        
        return {
            'total_records': len(self.df),
            'sources': self.df['source'].value_counts().to_dict(),
            'locations': self.df['location'].value_counts().to_dict(),
            'date_range': {
                'start': str(self.df['timestamp'].min()),
                'end': str(self.df['timestamp'].max())
            },
            'sentiment_distribution': self.df['sentiment'].value_counts().to_dict() if 'sentiment' in self.df.columns else {}
        }
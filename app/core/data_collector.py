import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
import tweepy
from textblob import TextBlob
import logging

from app.core.bias_corrector import BiasCorrector
from app.api.models import SentimentData
from app.config.settings import settings

logger = logging.getLogger(__name__)

from app.core.csv_data_loader import CSVDataLoader

class DataCollector:
    def __init__(self):
        self.bias_corrector = BiasCorrector()
        self.lagos_areas = settings.data_collection.lagos_areas
        self.security_keywords = settings.data_collection.security_keywords
        
        # Add CSV loader
        self.csv_loader = None
        try:
            self.csv_loader = CSVDataLoader("ikeja_security_social_media.csv")
            logger.info("CSV data loader initialized successfully")
        except Exception as e:
            logger.warning(f"CSV loader not available: {e}")
        
        # Initialize Twitter client
        self.twitter_client = None
        if settings.data_collection.twitter_bearer_token:
            self.twitter_client = tweepy.Client(
                bearer_token=settings.data_collection.twitter_bearer_token
            )
    
    def extract_location(self, text: str) -> str:
        """Extract Lagos area from text"""
        text_lower = text.lower()
        for area in self.lagos_areas:
            if area.lower() in text_lower:
                return area
        return 'Unknown'
    
    def categorize_security_issue(self, text: str) -> str:
        """Categorize the type of security issue"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['traffic', 'road', 'accident', 'jam']):
            return 'traffic'
        elif any(word in text_lower for word in ['crime', 'theft', 'robbery', 'steal']):
            return 'crime'
        elif any(word in text_lower for word in ['police', 'law', 'arrest']):
            return 'law_enforcement'
        elif any(word in text_lower for word in ['emergency', 'fire', 'medical']):
            return 'emergency'
        else:
            return 'general'
    
    def detect_language(self, text: str) -> str:
        """Detect if text contains Nigerian languages"""
        pidgin_words = self.security_keywords['pidgin']
        yoruba_words = self.security_keywords['yoruba']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in pidgin_words):
            return 'pidgin'
        elif any(word in text_lower for word in yoruba_words):
            return 'yoruba'
        else:
            return 'english'
    
    def is_security_related(self, text: str) -> bool:
        """Check if text is security-related"""
        text_lower = text.lower()
        
        for lang_keywords in self.security_keywords.values():
            if any(keyword in text_lower for keyword in lang_keywords):
                return True
        
        return False
    

    async def collect_twitter_data(self, limit: int = 100) -> List[SentimentData]:
        """Collect Twitter data"""
        results = []
        
        # Priority 1: Use CSV data if available
        if self.csv_loader:
            csv_data = self.csv_loader.get_sample_data(limit=limit, source_filter='twitter')
            if csv_data:
                logger.info(f"Using {len(csv_data)} records from CSV")
                return csv_data
        
        # Priority 2: Use real Twitter API if configured
        if self.twitter_client:
            try:
                # Real Twitter API implementation
                query = "Lagos OR Nigeria (security OR crime OR traffic OR safety) -is:retweet lang:en"
                tweets = tweepy.Paginator(
                    self.twitter_client.search_recent_tweets,
                    query=query,
                    max_results=min(100, limit),
                    tweet_fields=['created_at', 'public_metrics', 'geo']
                ).flatten(limit=limit)
                
                for tweet in tweets:
                    if self.is_security_related(tweet.text):
                        raw_sentiment = TextBlob(tweet.text).sentiment.polarity
                        adjusted_sentiment = self.bias_corrector.adjust_sentiment(raw_sentiment, 'twitter')
                        
                        data = SentimentData(
                            source='twitter',
                            text=tweet.text,
                            raw_sentiment=raw_sentiment,
                            adjusted_sentiment=adjusted_sentiment,
                            location=self.extract_location(tweet.text),
                            timestamp=tweet.created_at or datetime.now(),
                            confidence=0.7,
                            category=self.categorize_security_issue(tweet.text),
                            language=self.detect_language(tweet.text)
                        )
                        results.append(data)
                    
            except Exception as e:
                logger.error(f"Twitter collection error: {e}")
        
        # Priority 3: Fall back to hardcoded mock data
        return await self._generate_mock_twitter_data(limit)

    async def collect_all_csv_data(self, limit: int = 200) -> List[SentimentData]:
        """
        Collect all data from CSV regardless of source
        Useful for bulk testing
        """
        if not self.csv_loader:
            logger.warning("CSV loader not available")
            return []
        
        return self.csv_loader.get_sample_data(limit=limit)
    
    async def collect_news_data(self, limit: int = 50) -> List[SentimentData]:
        """Collect news data"""
        results = []
        
        # Nigerian news RSS feeds
        news_feeds = [
            'https://punchng.com/feed/',
            'https://www.vanguardngr.com/feed/',
            'https://www.premiumtimesng.com/feed/',
            'https://www.thecable.ng/feed'
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for feed_url in news_feeds:
                    try:
                        async with session.get(feed_url, timeout=10) as response:
                            if response.status == 200:
                                # Parse RSS feed (simplified for demo)
                                content = await response.text()
                                # In real implementation, use feedparser
                                articles = self._parse_rss_feed(content)
                                
                                for article in articles[:limit//len(news_feeds)]:
                                    if self.is_security_related(article['title'] + ' ' + article['description']):
                                        text = f"{article['title']} {article['description']}"
                                        raw_sentiment = TextBlob(text).sentiment.polarity
                                        adjusted_sentiment = self.bias_corrector.adjust_sentiment(raw_sentiment, 'news')
                                        
                                        data = SentimentData(
                                            source='news',
                                            text=text,
                                            raw_sentiment=raw_sentiment,
                                            adjusted_sentiment=adjusted_sentiment,
                                            location=self.extract_location(text),
                                            timestamp=article.get('published', datetime.now()),
                                            confidence=0.8,
                                            category=self.categorize_security_issue(text),
                                            language='english'
                                        )
                                        results.append(data)
                                        
                    except Exception as e:
                        logger.warning(f"Failed to fetch {feed_url}: {e}")
                        
        except Exception as e:
            logger.error(f"News collection error: {e}")
            return await self._generate_mock_news_data(limit)
        
        return results
    
    async def collect_government_data(self, limit: int = 20) -> List[SentimentData]:
        """Collect government announcements"""
        # Mock government data for demonstration
        return await self._generate_mock_government_data(limit)
    
    def _parse_rss_feed(self, content: str) -> List[Dict]:
        """Parse RSS feed content (simplified)"""
        # In real implementation, use feedparser library
        return [
            {
                'title': 'Lagos State announces new security measures',
                'description': 'Enhanced patrol systems deployed across major areas',
                'published': datetime.now() - timedelta(hours=2)
            }
        ]
    
    async def _generate_mock_twitter_data(self, limit: int) -> List[SentimentData]:
        """Generate mock Twitter data for demonstration"""
        mock_tweets = [
            "Traffic is terrible on Third Mainland Bridge today, police nowhere to be found #LagosTraffic",
            "Quick police response in Victoria Island incident. Great job! #LagosSafety",
            "Robbery incident reported in Surulere area, everyone please be careful",
            "LASTMA officers doing excellent work in Ikeja today #OneLagos",
            "Power outage causing security concerns in Yaba area",
            "Crime rate seems to be dropping in Ikoyi thanks to community policing",
            "Traffic light system in Lagos Island needs urgent repair",
            "Security checkpoint on Lagos-Ibadan expressway working well",
            "Pickpocket incident at Computer Village market today",
            "Emergency response team quick to arrive at Apapa accident scene"
        ]
        
        results = []
        for i, tweet in enumerate(mock_tweets[:limit]):
            raw_sentiment = TextBlob(tweet).sentiment.polarity
            adjusted_sentiment = self.bias_corrector.adjust_sentiment(raw_sentiment, 'twitter')
            
            data = SentimentData(
                source='twitter',
                text=tweet,
                raw_sentiment=raw_sentiment,
                adjusted_sentiment=adjusted_sentiment,
                location=self.extract_location(tweet),
                timestamp=datetime.now() - timedelta(hours=i),
                confidence=0.7 + (i * 0.02),
                category=self.categorize_security_issue(tweet),
                language=self.detect_language(tweet)
            )
            results.append(data)
        
        return results
    
    async def _generate_mock_news_data(self, limit: int) -> List[SentimentData]:
        """Generate mock news data"""
        mock_news = [
            "Lagos State government launches comprehensive security initiative across Victoria Island and Ikoyi areas",
            "Traffic congestion worsens in Ikeja as major road construction project begins",
            "Crime rate drops 15% in Surulere following successful community policing program implementation",
            "New intelligent traffic management system shows promising results on Lagos mainland",
            "Emergency response times improve by 25% across Lagos State following system upgrade"
        ]
        
        results = []
        for i, news in enumerate(mock_news[:limit]):
            raw_sentiment = TextBlob(news).sentiment.polarity
            adjusted_sentiment = self.bias_corrector.adjust_sentiment(raw_sentiment, 'news')
            
            data = SentimentData(
                source='news',
                text=news,
                raw_sentiment=raw_sentiment,
                adjusted_sentiment=adjusted_sentiment,
                location=self.extract_location(news),
                timestamp=datetime.now() - timedelta(hours=i*2),
                confidence=0.85,
                category=self.categorize_security_issue(news),
                language='english'
            )
            results.append(data)
        
        return results
    
    async def _generate_mock_government_data(self, limit: int) -> List[SentimentData]:
        """Generate mock government data"""
        mock_govt = [
            "Lagos State Security Trust Fund announces increased patrol frequency in high-traffic areas",
            "New community policing initiative launched in Surulere and Mushin local government areas",
            "Emergency response protocols updated for faster incident resolution across Lagos State"
        ]
        
        results = []
        for i, announcement in enumerate(mock_govt[:limit]):
            raw_sentiment = TextBlob(announcement).sentiment.polarity
            adjusted_sentiment = self.bias_corrector.adjust_sentiment(raw_sentiment, 'government')
            
            data = SentimentData(
                source='government',
                text=announcement,
                raw_sentiment=raw_sentiment,
                adjusted_sentiment=adjusted_sentiment,
                location=self.extract_location(announcement),
                timestamp=datetime.now() - timedelta(hours=i*6),
                confidence=0.9,
                category=self.categorize_security_issue(announcement),
                language='english'
            )
            results.append(data)
        
        return results
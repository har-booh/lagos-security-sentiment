import os
from dataclasses import dataclass
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    path: str = os.getenv('DATABASE_PATH', 'data/lagos_sentiment.db')
    backup_path: str = os.getenv('DATABASE_BACKUP_PATH', 'data/backups/')

@dataclass
class APIConfig:
    host: str = os.getenv('API_HOST', '0.0.0.0')
    port: int = int(os.getenv('API_PORT', 5000))
    debug: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    secret_key: str = os.getenv('SECRET_KEY', 'dev-secret-key')

@dataclass
class DataCollectionConfig:
    twitter_bearer_token: str = os.getenv('TWITTER_BEARER_TOKEN', '')
    news_api_key: str = os.getenv('NEWS_API_KEY', '')
    collection_interval_hours: int = int(os.getenv('COLLECTION_INTERVAL_HOURS', 4))
    
    # Lagos-specific configuration
    lagos_areas: List[str] = None
    security_keywords: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.lagos_areas is None:
            self.lagos_areas = [
                'Victoria Island', 'Ikeja', 'Surulere', 'Yaba', 'Ikoyi',
                'Lagos Island', 'Mainland', 'Apapa', 'Mushin', 'Alimosho',
                'Eti-Osa', 'Kosofe', 'Shomolu', 'Oshodi-Isolo', 'Agege'
            ]
        
        if self.security_keywords is None:
            self.security_keywords = {
                'english': [
                    'security', 'crime', 'theft', 'robbery', 'traffic', 'accident',
                    'police', 'safety', 'emergency', 'incident', 'violence'
                ],
                'pidgin': [
                    'wahala', 'gbege', 'kasala', 'palaba', 'scatter', 'burst'
                ],
                'yoruba': [
                    'ija', 'ole', 'wahala', 'opolopo', 'ewu'
                ]
            }

@dataclass
class BiasConfig:
    adjustment_factors: Dict[str, float] = None
    baseline_negativity: Dict[str, float] = None
    
    def __post_init__(self):
        if self.adjustment_factors is None:
            self.adjustment_factors = {
                'twitter': 0.7,
                'facebook': 0.8,
                'news': 0.6,
                'government': 1.2,
                'community': 1.0
            }
        
        if self.baseline_negativity is None:
            self.baseline_negativity = {
                'twitter': -0.35,
                'facebook': -0.25,
                'news': -0.45,
                'government': -0.05,
                'community': -0.15
            }

@dataclass
class AlertConfig:
    high_threshold: float = -0.5
    medium_threshold: float = -0.3
    minimum_sources: int = 3
    email_enabled: bool = True
    
    smtp_server: str = os.getenv('ALERT_EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('ALERT_EMAIL_SMTP_PORT', 587))
    email_username: str = os.getenv('ALERT_EMAIL_USERNAME', '')
    email_password: str = os.getenv('ALERT_EMAIL_PASSWORD', '')
    recipient_email: str = os.getenv('ALERT_RECIPIENT_EMAIL', '')

class Settings:
    """Application settings"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.data_collection = DataCollectionConfig()
        self.bias = BiasConfig()
        self.alerts = AlertConfig()
        
        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/lagos_sentiment.log')

# Global settings instance
settings = Settings()

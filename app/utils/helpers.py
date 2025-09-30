# =====================================
# FILE: app/utils/helpers.py
# =====================================

"""
Lagos Security Sentiment Analysis - Utility Helper Functions
Contains common utility functions used throughout the application
"""

import re
import unicodedata
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import logging
import hashlib
import json
from urllib.parse import urlparse
import requests
from textblob import TextBlob

logger = logging.getLogger(__name__)

# =====================================
# TEXT PROCESSING UTILITIES
# =====================================

def clean_text(text: str) -> str:
    """Clean and normalize text for analysis"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers (Nigerian format)
    text = re.sub(r'(\+234|0)[789][01]\d{8}', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'[.]{3,}', '...', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?@#-]', '', text)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    return text.strip()

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text, re.IGNORECASE)
    return [tag.lower() for tag in hashtags]

def extract_mentions(text: str) -> List[str]:
    """Extract mentions from text"""
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, text, re.IGNORECASE)
    return [mention.lower() for mention in mentions]

def detect_nigerian_language(text: str) -> str:
    """Detect if text contains Nigerian Pidgin or Yoruba words"""
    text_lower = text.lower()
    
    # Common Pidgin words
    pidgin_indicators = [
        'wahala', 'gbege', 'kasala', 'palaba', 'dey', 'wetin', 'abi', 'shey',
        'abeg', 'comot', 'naija', 'naira', 'oga', 'madam', 'pikin', 'japa',
        'sabi', 'waka', 'gist', 'hammer', 'scatter'
    ]
    
    # Common Yoruba words
    yoruba_indicators = [
        'omo', 'oko', 'obinrin', 'awa', 'eyin', 'won', 'mi', 'tire', 'wa',
        'ile', 'oja', 'eko', 'agba', 'omo', 'baba', 'mama', 'eko', 'iya'
    ]
    
    pidgin_count = sum(1 for word in pidgin_indicators if word in text_lower)
    yoruba_count = sum(1 for word in yoruba_indicators if word in text_lower)
    
    if pidgin_count > yoruba_count and pidgin_count > 0:
        return 'pidgin'
    elif yoruba_count > 0:
        return 'yoruba'
    else:
        return 'english'

def get_text_statistics(text: str) -> Dict[str, int]:
    """Get basic statistics about text"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    
    return {
        'character_count': len(text),
        'word_count': len(words),
        'sentence_count': len([s for s in sentences if s.strip()]),
        'hashtag_count': len(extract_hashtags(text)),
        'mention_count': len(extract_mentions(text)),
        'url_count': len(re.findall(r'http[s]?://\S+', text))
    }

# =====================================
# LAGOS GEOGRAPHIC UTILITIES
# =====================================

def get_lagos_areas() -> List[str]:
    """Get list of major Lagos areas"""
    return [
        'Victoria Island', 'Ikoyi', 'Lagos Island', 'Ikeja', 'Surulere',
        'Yaba', 'Apapa', 'Mushin', 'Alimosho', 'Agege', 'Eti-Osa',
        'Kosofe', 'Shomolu', 'Oshodi-Isolo', 'Ifako-Ijaiye', 'Somolu',
        'Lagos Mainland', 'Amuwo-Odofin', 'Ojo', 'Badagry'
    ]

def get_area_aliases() -> Dict[str, List[str]]:
    """Get alternative names/spellings for Lagos areas"""
    return {
        'Victoria Island': ['VI', 'V.I', 'vic island', 'victoria isl'],
        'Ikoyi': ['ikoyi island'],
        'Lagos Island': ['lagos isl', 'isale eko'],
        'Ikeja': ['ikeja gra', 'ikeja government'],
        'Surulere': ['suru lere', 'surulere lagos'],
        'Yaba': ['yaba college'],
        'Apapa': ['apapa port'],
        'Mushin': ['mushin lagos'],
        'Alimosho': ['alimosho lga'],
        'Agege': ['agege motor road'],
        'Eti-Osa': ['eti osa'],
        'Kosofe': ['kosofe lga'],
        'Shomolu': ['shomolu lga'],
        'Oshodi-Isolo': ['oshodi', 'isolo'],
        'Ifako-Ijaiye': ['ifako', 'ijaiye'],
        'Amuwo-Odofin': ['amuwo odofin', 'festac'],
        'Ojo': ['ojo cantonment'],
        'Badagry': ['badagry expressway']
    }

def extract_lagos_location(text: str) -> str:
    """Extract Lagos location from text with fuzzy matching"""
    text_lower = text.lower()
    areas = get_lagos_areas()
    aliases = get_area_aliases()
    
    # Direct area name match
    for area in areas:
        if area.lower() in text_lower:
            return area
    
    # Alias matching
    for area, area_aliases in aliases.items():
        for alias in area_aliases:
            if alias.lower() in text_lower:
                return area
    
    # Pattern matching for common formats
    # "in ikeja", "at yaba", "from surulere"
    location_patterns = [
        r'\b(?:in|at|from|near|around)\s+(\w+)',
        r'\b(\w+)\s+(?:area|region|district)',
        r'\b(\w+)\s+(?:road|street|avenue)'
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            # Check if match is a known area
            for area in areas:
                if match.lower() in area.lower() or area.lower().startswith(match.lower()):
                    return area
    
    return 'Unknown'

def get_area_coordinates() -> Dict[str, Tuple[float, float]]:
    """Get approximate coordinates for Lagos areas (lat, lng)"""
    return {
        'Victoria Island': (6.4281, 3.4219),
        'Ikoyi': (6.4581, 3.4396),
        'Lagos Island': (6.4550, 3.3841),
        'Ikeja': (6.6018, 3.3515),
        'Surulere': (6.4969, 3.3603),
        'Yaba': (6.5158, 3.3707),
        'Apapa': (6.4474, 3.3596),
        'Mushin': (6.5244, 3.3440),
        'Alimosho': (6.6050, 3.2500),
        'Agege': (6.6516, 3.3356),
        'Eti-Osa': (6.4604, 3.5106),
        'Kosofe': (6.4667, 3.3833),
        'Shomolu': (6.5374, 3.3834),
        'Oshodi-Isolo': (6.5244, 3.3204),
        'Ifako-Ijaiye': (6.6768, 3.2679),
        'Amuwo-Odofin': (6.4667, 3.2833),
        'Ojo': (6.4583, 3.1583),
        'Badagry': (6.4317, 2.8876)
    }

# =====================================
# SENTIMENT ANALYSIS UTILITIES
# =====================================

def calculate_sentiment_confidence(text: str, sentiment_score: float) -> float:
    """Calculate confidence score for sentiment analysis"""
    # Base confidence factors
    text_length = len(text.split())
    
    # Length factor (longer texts generally more reliable)
    length_factor = min(1.0, text_length / 10)  # Max confidence at 10+ words
    
    # Sentiment magnitude factor (extreme sentiments more confident)
    magnitude_factor = abs(sentiment_score)
    
    # Language clarity factor
    english_ratio = len(re.findall(r'[a-zA-Z]+', text)) / max(1, len(text.split()))
    clarity_factor = min(1.0, english_ratio)
    
    # Combine factors
    confidence = (length_factor * 0.4 + magnitude_factor * 0.4 + clarity_factor * 0.2)
    
    return min(0.95, max(0.1, confidence))  # Bound between 0.1 and 0.95

def is_security_relevant(text: str) -> bool:
    """Check if text is relevant to security topics"""
    security_keywords = {
        'direct': [
            'security', 'crime', 'theft', 'robbery', 'burglary', 'violence',
            'police', 'safety', 'dangerous', 'threat', 'attack', 'incident',
            'emergency', 'accident', 'fire', 'medical', 'ambulance'
        ],
        'traffic': [
            'traffic', 'road', 'highway', 'bridge', 'transport', 'bus',
            'taxi', 'okada', 'keke', 'danfo', 'jam', 'congestion'
        ],
        'locations': [
            'street', 'road', 'avenue', 'bridge', 'market', 'park',
            'station', 'airport', 'port', 'hospital', 'school'
        ],
        'nigerian': [
            'naija', 'lagos', 'wahala', 'gbege', 'kasala', 'palaba'
        ]
    }
    
    text_lower = text.lower()
    
    # Count relevant keywords
    total_matches = 0
    for category, keywords in security_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        total_matches += matches
    
    # Consider text relevant if it has 2+ security keywords
    return total_matches >= 2

def categorize_sentiment_topic(text: str) -> str:
    """Categorize the main topic of security-related text"""
    text_lower = text.lower()
    
    categories = {
        'traffic': [
            'traffic', 'road', 'highway', 'bridge', 'transport', 'bus',
            'taxi', 'okada', 'keke', 'danfo', 'jam', 'congestion', 'accident'
        ],
        'crime': [
            'crime', 'theft', 'robbery', 'burglary', 'steal', 'pickpocket',
            'fraud', 'scam', 'kidnap', 'violence', 'fight', 'attack'
        ],
        'law_enforcement': [
            'police', 'officer', 'arrest', 'station', 'patrol', 'checkpoint',
            'law', 'enforcement', 'authority', 'government'
        ],
        'emergency': [
            'emergency', 'fire', 'medical', 'ambulance', 'hospital',
            'accident', 'disaster', 'flood', 'rescue'
        ],
        'infrastructure': [
            'power', 'electricity', 'water', 'light', 'network',
            'internet', 'phone', 'service', 'facility'
        ]
    }
    
    # Count keywords for each category
    category_scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        category_scores[category] = score
    
    # Return category with highest score
    if max(category_scores.values()) > 0:
        return max(category_scores, key=category_scores.get)
    else:
        return 'general'

# =====================================
# DATA VALIDATION UTILITIES
# =====================================

def validate_sentiment_score(score: float) -> bool:
    """Validate sentiment score is within expected range"""
    return isinstance(score, (int, float)) and -1.0 <= score <= 1.0

def validate_confidence_score(confidence: float) -> bool:
    """Validate confidence score is within expected range"""
    return isinstance(confidence, (int, float)) and 0.0 <= confidence <= 1.0

def validate_timestamp(timestamp: datetime) -> bool:
    """Validate timestamp is reasonable (not too far in future/past)"""
    now = datetime.now()
    one_year_ago = now - timedelta(days=365)
    one_day_future = now + timedelta(days=1)
    
    return one_year_ago <= timestamp <= one_day_future

def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user text input"""
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potential script injection
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    return text.strip()

# =====================================
# HASH AND DEDUPLICATION UTILITIES
# =====================================

def generate_content_hash(text: str, source: str = "") -> str:
    """Generate hash for content deduplication"""
    # Normalize text for hashing
    normalized = clean_text(text).lower()
    content = f"{normalized}:{source}"
    
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity between two texts"""
    # Simple word-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def is_duplicate_content(text: str, existing_texts: List[str], threshold: float = 0.8) -> bool:
    """Check if content is duplicate of existing content"""
    for existing in existing_texts:
        similarity = calculate_text_similarity(text, existing)
        if similarity >= threshold:
            return True
    return False

# =====================================
# URL AND API UTILITIES
# =====================================

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def safe_api_request(url: str, timeout: int = 10, retries: int = 3) -> Optional[Dict]:
    """Make safe API request with error handling"""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"API request failed (attempt {attempt + 1}): {e}")
            if attempt == retries - 1:
                logger.error(f"All API request attempts failed for {url}")
                return None
    return None

# =====================================
# DATETIME UTILITIES
# =====================================

def format_timestamp(timestamp: datetime, format_type: str = 'iso') -> str:
    """Format timestamp in various formats"""
    formats = {
        'iso': timestamp.isoformat(),
        'human': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'date_only': timestamp.strftime('%Y-%m-%d'),
        'time_only': timestamp.strftime('%H:%M:%S'),
        'relative': get_relative_time(timestamp)
    }
    
    return formats.get(format_type, timestamp.isoformat())

def get_relative_time(timestamp: datetime) -> str:
    """Get human-readable relative time"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def parse_flexible_datetime(date_string: str) -> Optional[datetime]:
    """Parse datetime from various string formats"""
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse datetime: {date_string}")
    return None

# =====================================
# LOGGING AND DEBUG UTILITIES
# =====================================

def log_function_call(func_name: str, args: Dict[str, Any] = None, result: Any = None):
    """Log function call for debugging"""
    log_data = {
        'function': func_name,
        'timestamp': datetime.now().isoformat(),
        'args': args or {},
        'result_type': type(result).__name__ if result is not None else None
    }
    
    logger.debug(f"Function call: {json.dumps(log_data, default=str)}")

def performance_timer(func):
    """Decorator to time function execution"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"{func.__name__} executed in {duration:.3f} seconds")
        return result
    
    return wrapper

# =====================================
# CONFIGURATION UTILITIES
# =====================================

def load_json_config(file_path: str, default: Dict = None) -> Dict:
    """Load JSON configuration file with fallback to defaults"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load config from {file_path}: {e}")
        return default or {}

def save_json_config(data: Dict, file_path: str) -> bool:
    """Save configuration to JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Could not save config to {file_path}: {e}")
        return False

# =====================================
# DATA EXPORT UTILITIES
# =====================================

def export_to_csv(data: List[Dict], filename: str) -> bool:
    """Export data to CSV file"""
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"Data exported to {filename}")
        return True
    except Exception as e:
        logger.error(f"CSV export failed: {e}")
        return False

def export_to_json(data: Any, filename: str) -> bool:
    """Export data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Data exported to {filename}")
        return True
    except Exception as e:
        logger.error(f"JSON export failed: {e}")
        return False
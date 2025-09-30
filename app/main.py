"""
Main application entry point
"""

import asyncio
import logging
import os
import schedule
import threading
import time
from datetime import datetime

from app.api.routes import create_app
from app.core.sentiment_analyzer import SentimentAnalyzer
from app.config.settings import settings

# Configure logging
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_scheduled_analysis():
    """Run scheduled analysis in background"""
    analyzer = SentimentAnalyzer()
    
    def job():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(analyzer.run_analysis_cycle())
            loop.close()
            
            logger.info(f"Scheduled analysis completed: {result}")
            
        except Exception as e:
            logger.error(f"Scheduled analysis failed: {e}")
    
    # Schedule analysis based on configuration
    interval = settings.data_collection.collection_interval_hours
    schedule.every(interval).hours.do(job)
    
    # Run initial analysis
    logger.info("Running initial data collection...")
    job()
    
    # Keep running scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def main():
    """Main application entry point"""
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Create Flask app
    app = create_app()
    
    # Start background scheduler
    logger.info("Starting background analysis scheduler")
    scheduler_thread = threading.Thread(target=run_scheduled_analysis, daemon=True)
    scheduler_thread.start()
    
    # Start Flask app
    logger.info(f"Starting Lagos Security Sentiment Analysis API on {settings.api.host}:{settings.api.port}")
    app.run(
        host=settings.api.host,
        port=settings.api.port,
        debug=settings.api.debug,
        use_reloader=False  # Disable reloader to prevent double scheduling
    )

if __name__ == '__main__':
    main()
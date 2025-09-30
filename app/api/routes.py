from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import logging
from datetime import datetime

from app.core.sentiment_analyzer import SentimentAnalyzer
from app.config.settings import settings

logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = settings.api.secret_key
    
    # Enable CORS
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected'
        })
    
    @app.route('/api/sentiment/current', methods=['GET'])
    def get_current_sentiment():
        """Get current overall sentiment"""
        try:
            status = analyzer.get_current_status()
            return jsonify(status)
            
        except Exception as e:
            logger.error(f"Error getting current sentiment: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sentiment/area/<area_name>', methods=['GET'])
    def get_area_sentiment(area_name):
        """Get sentiment for specific area"""
        try:
            recent_data = analyzer.db.get_recent_sentiment(24)
            area_data = [item for item in recent_data if item['location'] == area_name]
            
            if not area_data:
                return jsonify({
                    'area': area_name,
                    'sentiment': 0.0,
                    'confidence': 0.0,
                    'source_count': 0,
                    'recent_items': []
                })
            
            sentiments = [item['adjusted_sentiment'] for item in area_data]
            confidences = [item['confidence'] for item in area_data]
            
            avg_sentiment = sum(sentiments) / len(sentiments)
            avg_confidence = sum(confidences) / len(confidences)
            
            return jsonify({
                'area': area_name,
                'sentiment': round(avg_sentiment, 3),
                'confidence': round(avg_confidence, 3),
                'source_count': len(area_data),
                'recent_items': area_data[:10]
            })
            
        except Exception as e:
            logger.error(f"Error getting area sentiment: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/alerts/active', methods=['GET'])
    def get_active_alerts():
        """Get current active alerts"""
        try:
            alerts = analyzer.db.get_active_alerts()
            
            # Format alerts for API response
            formatted_alerts = []
            for alert in alerts:
                formatted_alerts.append({
                    'id': alert['id'],
                    'area': alert['area'],
                    'message': alert['message'],
                    'severity': alert['severity'],
                    'confidence': round(alert['confidence'], 3),
                    'type': alert['alert_type'],
                    'time': datetime.fromisoformat(alert['timestamp']).strftime('%H:%M')
                })
            
            return jsonify(formatted_alerts)
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/trends/weekly', methods=['GET'])
    def get_weekly_trends():
        """Get weekly sentiment trends"""
        try:
            trends = analyzer.db.get_trends(7)
            return jsonify(trends)
            
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/areas', methods=['GET'])
    def get_area_analysis():
        """Get sentiment analysis by area"""
        try:
            areas = analyzer.db.get_area_analysis(24)
            return jsonify(areas)
            
        except Exception as e:
            logger.error(f"Error getting area analysis: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/sources', methods=['GET'])
    def get_source_breakdown():
        """Get breakdown of data sources"""
        try:
            sources = analyzer.db.get_source_breakdown(24)
            return jsonify(sources)
            
        except Exception as e:
            logger.error(f"Error getting source breakdown: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analysis/run', methods=['POST'])
    def trigger_analysis():
        """Manually trigger analysis cycle"""
        try:
            # Run async analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(analyzer.run_analysis_cycle())
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error running analysis: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bias/correction/<source>', methods=['GET'])
    def get_bias_correction_info(source):
        """Get bias correction information for a source"""
        try:
            bias_info = analyzer.collector.bias_corrector.get_correction_info(source)
            return jsonify(bias_info)
            
        except Exception as e:
            logger.error(f"Error getting bias info: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

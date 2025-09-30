from typing import Dict
from app.config.settings import settings

class BiasCorrector:
    """Handles bias correction for different data sources"""
    
    def __init__(self):
        self.adjustment_factors = settings.bias.adjustment_factors
        self.baseline_negativity = settings.bias.baseline_negativity
    
    def adjust_sentiment(self, raw_sentiment: float, source: str) -> float:
        """Apply bias correction to raw sentiment"""
        adjustment_factor = self.adjustment_factors.get(source, 1.0)
        baseline = self.baseline_negativity.get(source, -0.2)
        
        # Normalize against baseline
        normalized = raw_sentiment - baseline
        
        if raw_sentiment < 0:  # Negative sentiment
            adjusted = normalized * adjustment_factor + baseline
        else:  # Positive sentiment gets slight boost
            adjusted = normalized * 1.1 + baseline
            
        return max(-1, min(1, adjusted))  # Keep within bounds
    
    def get_correction_info(self, source: str) -> Dict:
        """Get bias correction information for a source"""
        return {
            'source': source,
            'adjustment_factor': self.adjustment_factors.get(source, 1.0),
            'baseline_negativity': self.baseline_negativity.get(source, -0.2),
            'description': self._get_bias_description(source)
        }
    
    def _get_bias_description(self, source: str) -> str:
        """Get human-readable bias description"""
        descriptions = {
            'twitter': 'High negative bias - reduces negative weight by 30%',
            'facebook': 'Medium negative bias - reduces negative weight by 20%',
            'news': 'High negative bias - reduces negative weight by 40%',
            'government': 'Positive bias - increases negative weight by 20%',
            'community': 'Balanced - no adjustment applied'
        }
        return descriptions.get(source, 'Unknown bias pattern')
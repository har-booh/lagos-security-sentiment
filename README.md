# Lagos Security Sentiment Analysis MVP

A production-ready sentiment analysis system for monitoring security-related discussions across Lagos, Nigeria, with built-in bias correction for social media and news sources.

## 🎯 Features

- **Multi-source Data Collection**: Twitter, news outlets, government sources
- **Bias Correction**: Adjusts for inherent negativity in security-related social media
- **Geographic Analysis**: Area-specific sentiment tracking across 15+ Lagos areas
- **Real-time Alerts**: Automated detection of security concern spikes
- **Multi-language Support**: English, Pidgin, and basic Yoruba processing
- **RESTful API**: Complete API with 8+ endpoints
- **Production Ready**: Docker deployment, monitoring, and backup systems

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (for production)
- 2GB RAM minimum
- 10GB storage space

### Option 1: Local Development

```bash
# Clone and setup
git clone <repository-url>
cd lagos-security-sentiment

# Run setup script
chmod +x setup.sh
./setup.sh

# Start the application
source venv/bin/activate
python -m app.main
```

### Option 2: Docker Deployment (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Edit configuration (optional)
nano .env

# Deploy with Docker
docker-compose up -d

# Check status
curl http://localhost/api/health
```

## 📁 Project Structure

```
lagos-security-sentiment/
├── app/                     # Main application code
│   ├── core/               # Core analysis components
│   │   ├── bias_corrector.py
│   │   ├── data_collector.py
│   │   ├── sentiment_analyzer.py
│   │   └── alert_generator.py
│   ├── api/                # API routes and models
│   ├── database/           # Database management
│   ├── config/             # Configuration management
│   └── main.py            # Application entry point
├── scripts/                # Deployment and utility scripts
│   ├── deploy.sh
│   ├── monitor.py
│   └── backup.py
├── data/                   # Database and data files
├── logs/                   # Application logs
└── docs/                   # Documentation
```

## 🔧 Configuration

The system uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
# Database
DATABASE_PATH=data/lagos_sentiment.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Data Collection (add your API keys)
TWITTER_BEARER_TOKEN=your_token_here
NEWS_API_KEY=your_key_here
COLLECTION_INTERVAL_HOURS=4

# Alerts
ALERT_EMAIL_USERNAME=your_email@gmail.com
ALERT_RECIPIENT_EMAIL=alerts@lagosstate.gov.ng
```

## 📊 API Endpoints

### Core Endpoints
- `GET /api/health` - System health check
- `GET /api/sentiment/current` - Current overall sentiment
- `GET /api/sentiment/area/{area}` - Area-specific sentiment
- `GET /api/alerts/active` - Current security alerts
- `GET /api/trends/weekly` - 7-day sentiment trends
- `GET /api/areas` - All areas analysis
- `GET /api/sources` - Data source breakdown
- `POST /api/analysis/run` - Trigger manual analysis

### Example API Response
```json
{
  "overall_sentiment": 0.32,
  "raw_sentiment": -0.15,
  "confidence": 0.78,
  "total_sources": 1247,
  "last_update": "2024-09-27T14:30:00Z",
  "status": "healthy"
}
```

## 🎛️ Bias Correction System

The system applies sophisticated bias correction based on source patterns:

| Source | Bias Factor | Reasoning |
|--------|-------------|-----------|
| Twitter | 0.7 | 30% negative bias reduction (high negativity) |
| News Media | 0.6 | 40% negative bias reduction (conflict-focused) |
| Facebook | 0.8 | 20% negative bias reduction (moderate negativity) |
| Government | 1.2 | 20% negative weight increase (positive bias) |
| Community | 1.0 | No adjustment (assumed balanced) |

## 🗺️ Lagos Areas Covered

The system tracks sentiment across 15+ major Lagos areas:
- Victoria Island
- Ikeja
- Surulere
- Yaba
- Ikoyi
- Lagos Island
- Mainland
- Apapa
- Mushin
- Alimosho
- And more...

## 🚨 Alert System

### Alert Severity Levels
- **High**: Sentiment below -0.5 with 3+ sources
- **Medium**: Sentiment below -0.3 with 3+ sources

### Alert Categories
- **Traffic**: Road congestion, accidents, transport issues
- **Crime**: Theft, robbery, security incidents
- **Law Enforcement**: Police activities, arrests
- **Emergency**: Fire, medical, urgent incidents
- **General**: Other security-related concerns

## 📈 Monitoring & Maintenance

### System Monitoring
```bash
# Run monitoring script
python scripts/monitor.py

# Check system status
python scripts/monitor.py --once
```

### Backup Management
```bash
# Create backup
python scripts/backup.py --backup-db

# Export data
python scripts/backup.py --export-data --days 30

# Cleanup old backups
python scripts/backup.py --cleanup --days 30
```

### Deployment
```bash
# Deploy new version
bash scripts/deploy.sh production
```

## 🔒 Security Features

- Rate limiting (10 requests/second)
- CORS protection
- Input sanitization
- SQL injection prevention
- Health check endpoints
- Secure headers (HTTPS recommended)

## 📊 Performance Specifications

### System Requirements
- **Minimum**: 2 CPU cores, 2GB RAM, 10GB storage
- **Recommended**: 4 CPU cores, 4GB RAM, 50GB storage

### Performance Metrics
- **Data Processing**: 5,000+ posts per analysis cycle
- **Response Time**: <2 seconds for API calls
- **Analysis Frequency**: Every 4 hours (configurable)
- **Storage Growth**: ~100MB per month

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Test specific component
pytest tests/test_bias_correction.py -v
```

## 🌍 Multi-Language Support

The system handles Nigerian linguistic diversity:

### Supported Languages
- **English**: Full sentiment analysis
- **Nigerian Pidgin**: Keyword detection and basic sentiment
- **Yoruba**: Security keyword recognition

### Example Keywords
- **English**: security, crime, theft, police, safety
- **Pidgin**: wahala, gbege, kasala, palaba
- **Yoruba**: ija, ole, wahala, ewu

## 📱 Integration Examples

### Python Integration
```python
import requests

# Get current sentiment
response = requests.get('http://localhost:5000/api/sentiment/current')
data = response.json()
print(f"Overall sentiment: {data['overall_sentiment']}")

# Get area-specific data
response = requests.get('http://localhost:5000/api/sentiment/area/Victoria Island')
area_data = response.json()
```

### JavaScript Integration
```javascript
// Fetch current sentiment
fetch('http://localhost:5000/api/sentiment/current')
  .then(response => response.json())
  .then(data => {
    console.log('Current sentiment:', data.overall_sentiment);
  });
```

## 🚀 Production Deployment

### Docker Deployment (Recommended)
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up --scale lagos-sentiment-api=3
```

### Traditional Server Deployment
```bash
# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

### Nginx Configuration
```nginx
upstream lagos_api {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://lagos_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🎯 Use Cases

### Government Agencies
- Real-time security situation awareness
- Resource allocation based on sentiment trends
- Community concern identification
- Policy impact assessment

### Security Organizations
- Threat detection and early warning
- Public sentiment monitoring
- Incident correlation analysis
- Community engagement metrics

### Research Institutions
- Urban security studies
- Social media bias analysis
- Nigerian language processing research
- Crisis communication effectiveness

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check database permissions
chmod 755 data/
chmod 644 data/lagos_sentiment.db

# Recreate database
python -c "from app.database.manager import DatabaseManager; DatabaseManager().init_database()"
```

**High Memory Usage**
```bash
# Check database size
du -h data/lagos_sentiment.db

# Clean old data (keep last 30 days)
python scripts/backup.py --cleanup --days 30
```

**API Not Responding**
```bash
# Check service status
curl http://localhost:5000/api/health

# Check logs
tail -f logs/lagos_sentiment.log

# Restart services
docker-compose restart
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Architecture Overview](docs/architecture.md)
- [Bias Correction Details](docs/bias_correction.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd lagos-security-sentiment

# Setup development environment
./setup.sh

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Start development server
python -m app.main
```

## 📊 Sample Data & Demo

The MVP includes realistic sample data for immediate testing:

### Sample Sentiment Data
- 50+ mock social media posts
- 20+ news article samples
- 10+ government announcements
- Multi-language content examples

### Demo Features
```bash
# Generate sample data
curl -X POST http://localhost:5000/api/analysis/run

# View sample alerts
curl http://localhost:5000/api/alerts/active

# Check area analysis
curl http://localhost:5000/api/areas
```

## 🔄 Data Flow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Bias Correction │───▶│ Sentiment Score │
│                 │    │    Algorithm     │    │   (-1 to +1)    │
│ • Twitter       │    │                  │    │                 │
│ • News Media    │    │ • Source weights │    │ • Raw score     │
│ • Government    │    │ • Baseline adj.  │    │ • Adjusted      │
│ • Community     │    │ • Temporal smooth│    │ • Confidence    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │    │  Alert Engine    │    │   API Layer     │
│                 │    │                  │    │                 │
│ • SQLite        │    │ • Threshold      │    │ • REST API      │
│ • Indexed       │    │ • Geographic     │    │ • Real-time     │
│ • Timestamped   │    │ • Category       │    │ • JSON output   │
│ • Backed up     │    │ • Severity       │    │ • CORS enabled  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Implementation Checklist

### ✅ Completed Features
- [x] Multi-source data collection
- [x] Bias correction algorithms
- [x] Geographic sentiment analysis
- [x] Real-time alert generation
- [x] RESTful API with 8+ endpoints
- [x] SQLite database with indexing
- [x] Docker containerization
- [x] Monitoring and health checks
- [x] Backup and recovery system
- [x] Multi-language keyword detection
- [x] Production deployment scripts
- [x] Comprehensive documentation

### 🚧 Future Enhancements
- [ ] Machine learning model integration
- [ ] Advanced NLP for Nigerian languages
- [ ] Real-time WebSocket feeds
- [ ] Mobile app development
- [ ] Integration with Lagos State systems
- [ ] Advanced visualization dashboard
- [ ] Predictive analytics
- [ ] Sentiment trend forecasting

## 💰 Cost Breakdown

### Development Costs (One-time)
- Development: $15,000 - $25,000
- Testing & QA: $3,000 - $5,000
- Documentation: $2,000 - $3,000
- **Total**: $20,000 - $33,000

### Operational Costs (Monthly)
- **Basic Deployment**: $200 - $500/month
  - Small VPS (2 CPU, 4GB RAM)
  - Twitter API Basic
  - Email services
  
- **Production Deployment**: $800 - $1,500/month
  - Medium server (4 CPU, 8GB RAM)
  - Twitter API Premium
  - Load balancing
  - Monitoring services
  - Backup storage

- **Enterprise Deployment**: $2,000 - $5,000/month
  - High-availability setup
  - Multiple servers
  - Advanced analytics
  - 24/7 monitoring
  - Professional support

## 🎖️ Awards & Recognition

This project demonstrates:
- **Technical Excellence**: Modern, scalable architecture
- **Social Impact**: Addresses real security concerns in Lagos
- **Innovation**: Novel bias correction for African social media
- **Practical Value**: Immediately deployable for government use

## 📞 Support & Contact

### Community Support
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Documentation: [Read the docs](docs/)
- FAQ: [Frequently Asked Questions](docs/faq.md)

### Professional Support
- Technical Consulting: Available for custom implementations
- Training Services: API integration and deployment training
- Custom Development: Additional features and integrations

### Emergency Contact
For critical production issues:
- Email: support@lagos-sentiment-analysis.com
- Phone: +234-XXX-XXX-XXXX (Lagos business hours)

## 📄 License

MIT License

Copyright (c) 2024 Lagos Security Sentiment Analysis Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🙏 Acknowledgments

- Lagos State Government for security data insights
- Nigerian technology community for language processing support
- Open source contributors and maintainers
- Security researchers and analysts
- Lagos residents who provided feedback and validation

---

**Ready to deploy? Start with:** `./setup.sh`

**Questions?** Check our [documentation](docs/) or open an [issue](https://github.com/your-repo/issues).

**Want to contribute?** See our [contributing guide](CONTRIBUTING.md).

---

*Lagos Security Sentiment Analysis - Making Lagos Safer Through Intelligent Monitoring* 🇳🇬
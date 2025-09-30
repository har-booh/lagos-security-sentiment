# Test imports
python -c "from app.api.models import SentimentData, SecurityAlert; print('✅ Models imported successfully')"

# Initialize database
python -c "from app.database.manager import DatabaseManager; db = DatabaseManager(); print('✅ Database initialized')"

# Test the whole app
python -c "import app; print(f'✅ App version: {app.__version__}')"
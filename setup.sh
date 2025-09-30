#!/bin/bash

# =====================================
# Lagos Security Sentiment Analysis - Setup Script
# Automated setup for development and production environments
# =====================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.9"
PROJECT_NAME="Lagos Security Sentiment Analysis"
VENV_NAME="venv"
LOG_FILE="setup.log"

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print section headers
print_header() {
    echo ""
    print_color $CYAN "======================================"
    print_color $CYAN "$1"
    print_color $CYAN "======================================"
    echo ""
}

# Function to print status
print_status() {
    print_color $BLUE "📋 $1"
}

print_success() {
    print_color $GREEN "✅ $1"
}

print_warning() {
    print_color $YELLOW "⚠️  $1"
}

print_error() {
    print_color $RED "❌ $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V | head -n1 | grep -q "^$2$"
}

# Function to check Python version
check_python() {
    print_status "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        print_color $YELLOW "Please install Python ${PYTHON_MIN_VERSION}+ from https://python.org"
        exit 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_status "Found Python $PYTHON_VERSION"
    
    # Check minimum version
    if version_ge "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        print_success "Python version meets requirements (>= $PYTHON_MIN_VERSION)"
    else
        print_error "Python $PYTHON_VERSION is too old. Minimum required: $PYTHON_MIN_VERSION"
        exit 1
    fi
}

# Function to check pip
check_pip() {
    print_status "Checking pip installation..."
    
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_warning "pip is not installed. Installing pip..."
        
        if command_exists curl; then
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            $PYTHON_CMD get-pip.py
            rm get-pip.py
        else
            print_error "curl is required to install pip. Please install curl or pip manually."
            exit 1
        fi
    fi
    
    print_success "pip is available"
}

# Function to create virtual environment
create_venv() {
    print_status "Setting up virtual environment..."
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment already exists at $VENV_NAME"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf "$VENV_NAME"
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi
    
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_NAME"
    
    if [ ! -d "$VENV_NAME" ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment created at $VENV_NAME"
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    # Determine activation script path
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        ACTIVATE_SCRIPT="$VENV_NAME/Scripts/activate"
    else
        ACTIVATE_SCRIPT="$VENV_NAME/bin/activate"
    fi
    
    if [ ! -f "$ACTIVATE_SCRIPT" ]; then
        print_error "Virtual environment activation script not found"
        exit 1
    fi
    
    source "$ACTIVATE_SCRIPT"
    print_success "Virtual environment activated"
}

# Function to upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    python -m pip install --upgrade pip
    print_success "pip upgraded"
}

# Function to install requirements
install_requirements() {
    print_status "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_status "Installing base requirements..."
    python -m pip install -r requirements.txt
    
    # Ask about development dependencies
    echo ""
    read -p "Install development dependencies? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "requirements-dev.txt" ]; then
            print_status "Installing development dependencies..."
            python -m pip install -r requirements-dev.txt
            print_success "Development dependencies installed"
        else
            print_warning "requirements-dev.txt not found, skipping"
        fi
    fi
    
    print_success "Python dependencies installed"
}

# Function to download TextBlob corpora
setup_textblob() {
    print_status "Setting up TextBlob corpora..."
    python -m textblob.download_corpora
    print_success "TextBlob corpora downloaded"
}

# Function to create directories
create_directories() {
    print_status "Creating project directories..."
    
    # Create necessary directories
    mkdir -p data
    mkdir -p logs
    mkdir -p backups
    mkdir -p config
    
    # Create .gitkeep files for empty directories
    touch data/.gitkeep
    touch logs/.gitkeep
    touch backups/.gitkeep
    
    print_success "Project directories created"
}

# Function to setup environment file
setup_env_file() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment file created from template"
            print_warning "Please edit .env file with your configuration"
        else
            print_status "Creating basic .env file..."
            cat > .env << EOF
# Lagos Security Sentiment Analysis Configuration

# Database Configuration
DATABASE_PATH=data/lagos_sentiment.db

# API Configuration
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000

# Data Collection Settings
TWITTER_BEARER_TOKEN=
NEWS_API_KEY=
COLLECTION_INTERVAL_HOURS=4

# Alert Settings
ALERT_EMAIL_USERNAME=
ALERT_EMAIL_PASSWORD=
ALERT_RECIPIENT_EMAIL=

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/lagos_sentiment.log
EOF
            print_success "Basic .env file created"
            print_warning "Please edit .env file with your API keys and configuration"
        fi
    else
        print_warning ".env file already exists, skipping"
    fi
}

# Function to initialize database
init_database() {
    print_status "Initializing database..."
    
    python -c "
try:
    from app.database.manager import DatabaseManager
    db = DatabaseManager()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    exit(1)
" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "Database initialized"
    else
        print_error "Database initialization failed. Check $LOG_FILE for details."
        exit 1
    fi
}

# Function to run initial data collection
run_initial_data_collection() {
    echo ""
    read -p "Run initial data collection? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Running initial data collection..."
        
        python -c "
import asyncio
from app.core.sentiment_analyzer import SentimentAnalyzer

async def init_data():
    try:
        analyzer = SentimentAnalyzer()
        result = await analyzer.run_analysis_cycle()
        print(f'✅ Initial data collection completed: {result}')
        return True
    except Exception as e:
        print(f'❌ Initial data collection failed: {e}')
        return False

success = asyncio.run(init_data())
exit(0 if success else 1)
" 2>> "$LOG_FILE"
        
        if [ $? -eq 0 ]; then
            print_success "Initial data collection completed"
        else
            print_warning "Initial data collection failed. You can run it later with: python -m app.main"
        fi
    fi
}

# Function to check optional dependencies
check_optional_dependencies() {
    print_status "Checking optional dependencies..."
    
    # Check for Docker
    if command_exists docker; then
        print_success "Docker is available for containerized deployment"
    else
        print_warning "Docker not found. Install Docker for containerized deployment."
    fi
    
    # Check for git
    if command_exists git; then
        print_success "Git is available for version control"
    else
        print_warning "Git not found. Install Git for version control."
    fi
    
    # Check for curl
    if command_exists curl; then
        print_success "curl is available for API testing"
    else
        print_warning "curl not found. Install curl for API testing."
    fi
}

# Function to run tests
run_tests() {
    echo ""
    read -p "Run tests to verify installation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Running tests..."
        
        if python -m pytest tests/ -v --tb=short 2>> "$LOG_FILE"; then
            print_success "All tests passed"
        else
            print_warning "Some tests failed. Check $LOG_FILE for details."
        fi
    fi
}

# Function to display next steps
show_next_steps() {
    print_header "🎉 Setup Complete!"
    
    echo "Your Lagos Security Sentiment Analysis system is ready!"
    echo ""
    print_color $GREEN "Next Steps:"
    echo ""
    print_color $YELLOW "1. Activate the virtual environment:"
    echo "   source $VENV_NAME/bin/activate"
    echo ""
    print_color $YELLOW "2. Edit configuration (important!):"
    echo "   nano .env"
    echo "   # Add your Twitter API keys and other settings"
    echo ""
    print_color $YELLOW "3. Start the application:"
    echo "   python -m app.main"
    echo ""
    print_color $YELLOW "4. Test the API:"
    echo "   curl http://localhost:5000/api/health"
    echo ""
    print_color $CYAN "Optional - Production Deployment:"
    echo "   docker-compose up -d"
    echo ""
    print_color $CYAN "Optional - Development Tools:"
    echo "   pytest                    # Run tests"
    echo "   black app/ scripts/       # Format code"
    echo "   python scripts/monitor.py # Monitor system"
    echo ""
    print_color $PURPLE "Documentation:"
    echo "   README.md                 # Full documentation"
    echo "   CONTRIBUTING.md           # Contribution guide"
    echo "   docs/                     # Additional docs"
    echo ""
    print_color $GREEN "API will be available at: http://localhost:5000"
    echo ""
}

# Function to handle cleanup on error
cleanup_on_error() {
    print_error "Setup failed. Cleaning up..."
    # Add cleanup commands here if needed
    exit 1
}

# Function to check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check available disk space (require at least 1GB)
    if command_exists df; then
        available_space=$(df . | tail -1 | awk '{print $4}')
        if [ "$available_space" -lt 1048576 ]; then  # 1GB in KB
            print_warning "Low disk space. Recommend at least 1GB free space."
        fi
    fi
    
    # Check memory (warn if less than 2GB)
    if command_exists free; then
        total_mem=$(free -m | awk 'NR==2{print $2}')
        if [ "$total_mem" -lt 2048 ]; then
            print_warning "Limited RAM detected. Recommend at least 2GB RAM."
        fi
    fi
    
    print_success "System requirements check completed"
}

# Main setup function
main() {
    # Setup error handling
    trap cleanup_on_error ERR
    
    # Clear log file
    > "$LOG_FILE"
    
    print_header "🚀 $PROJECT_NAME Setup"
    
    print_color $YELLOW "This script will set up your Lagos Security Sentiment Analysis environment."
    print_color $YELLOW "Setup log will be written to: $LOG_FILE"
    echo ""
    
    # Run setup steps
    check_system_requirements
    check_python
    check_pip
    create_venv
    activate_venv
    upgrade_pip
    install_requirements
    setup_textblob
    create_directories
    setup_env_file
    init_database
    check_optional_dependencies
    run_initial_data_collection
    run_tests
    
    # Show completion message
    show_next_steps
}

# Parse command line arguments
SKIP_TESTS=false
SKIP_DATA=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-data)
            SKIP_DATA=true
            shift
            ;;
        --help|-h)
            echo "Lagos Security Sentiment Analysis Setup Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --skip-tests    Skip running tests during setup"
            echo "  --skip-data     Skip initial data collection"
            echo "  --help, -h      Show this help message"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main setup
main

print_color $GREEN "🎉 Lagos Security Sentiment Analysis is ready!"
print_color $GREEN "Thank you for helping make Lagos safer! 🇳🇬"
#!/bin/bash

# BaiKaoTong AI Writing Platform - Local Deployment Script
# This script sets up the platform for local development

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="BaiKaoTong AI Writing Platform"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOYMENT_DIR="$BASE_DIR/deployment"
CONFIG_DIR="$DEPLOYMENT_DIR/config"
SCRIPTS_DIR="$DEPLOYMENT_DIR/scripts"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        log_error "Node.js version 16 or higher is required. Current version: $(node --version)"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        log_error "pip is not installed. Please install pip."
        exit 1
    fi
    
    log_success "System requirements check passed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$BASE_DIR/data"
    mkdir -p "$BASE_DIR/logs"
    mkdir -p "$BASE_DIR/uploads"
    mkdir -p "$BASE_DIR/backups"
    
    log_success "Directories created"
}

# Set up environment
setup_environment() {
    log "Setting up environment configuration..."
    
    # Copy local environment file if it doesn't exist
    if [ ! -f "$BASE_DIR/.env" ]; then
        if [ -f "$CONFIG_DIR/.env.local" ]; then
            cp "$CONFIG_DIR/.env.local" "$BASE_DIR/.env"
            log_success "Local environment configuration copied"
        else
            log_warning "Local environment template not found, copying example"
            cp "$CONFIG_DIR/.env.example" "$BASE_DIR/.env"
        fi
    else
        log_warning "Environment file already exists, skipping"
    fi
    
    # Prompt user to update configuration
    log_warning "Please update the .env file with your configuration:"
    log_warning "  - DOUBAO_API_KEY: Your Doubao AI API key"
    log_warning "  - SECRET_KEY: A secure secret key"
    log_warning "  - Other settings as needed"
}

# Install backend dependencies
install_backend() {
    log "Installing backend dependencies..."
    
    cd "$BASE_DIR/backend"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Backend dependencies installed"
    else
        log_error "Backend requirements.txt not found"
        exit 1
    fi
    
    # Deactivate virtual environment
    deactivate
}

# Install frontend dependencies
install_frontend() {
    log "Installing frontend dependencies..."
    
    cd "$BASE_DIR/frontend"
    
    if [ -f "package.json" ]; then
        npm install
        log_success "Frontend dependencies installed"
    else
        log_error "Frontend package.json not found"
        exit 1
    fi
}

# Initialize database
init_database() {
    log "Initializing database..."
    
    cd "$BASE_DIR/backend"
    source venv/bin/activate
    
    # Run database migration
    export PYTHONPATH="$BASE_DIR/backend/src"
    python3 "$SCRIPTS_DIR/migrate-db.py"
    
    if [ $? -eq 0 ]; then
        log_success "Database initialized successfully"
    else
        log_error "Database initialization failed"
        exit 1
    fi
    
    deactivate
}

# Install PM2 globally
install_pm2() {
    log "Installing PM2 process manager..."
    
    if ! command -v pm2 &> /dev/null; then
        npm install -g pm2
        log_success "PM2 installed successfully"
    else
        log_warning "PM2 already installed"
    fi
}

# Start services
start_services() {
    log "Starting services..."
    
    cd "$BASE_DIR"
    
    # Start PM2 services
    pm2 start "$CONFIG_DIR/local-ecosystem.config.js"
    
    # Save PM2 configuration
    pm2 save
    
    log_success "Services started successfully"
    
    # Show status
    pm2 status
    
    # Show access URLs
    log ""
    log_success "🎉 Local deployment completed successfully!"
    log ""
    log "Access your application at:"
    log "  Frontend: ${GREEN}http://localhost:3000${NC}"
    log "  Backend API: ${GREEN}http://localhost:5000${NC}"
    log ""
    log "Useful commands:"
    log "  View logs: ${YELLOW}pm2 logs${NC}"
    log "  Stop services: ${YELLOW}pm2 stop all${NC}"
    log "  Restart services: ${YELLOW}pm2 restart all${NC}"
    log "  Monitor services: ${YELLOW}pm2 monit${NC}"
}

# Main deployment function
main() {
    log "Starting local deployment of $PROJECT_NAME"
    log "Base directory: $BASE_DIR"
    
    check_requirements
    create_directories
    setup_environment
    install_backend
    install_frontend
    install_pm2
    init_database
    start_services
    
    log_success "Local deployment completed!"
}

# Handle script interruption
cleanup() {
    log_warning "Deployment interrupted"
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
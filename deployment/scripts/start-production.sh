#!/bin/bash

# BaiKaoTong AI Writing Platform - Production Start Script
# This script starts the platform in production mode inside Docker container

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Wait for database to be ready
wait_for_db() {
    log "Waiting for database to be ready..."
    
    if [ "$DB_TYPE" = "postgresql" ]; then
        # Wait for PostgreSQL
        until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
            log "PostgreSQL is unavailable - sleeping"
            sleep 2
        done
        log_success "PostgreSQL is ready"
    fi
}

# Initialize database
init_database() {
    log "Initializing database..."
    
    # Run database migrations
    cd /app
    python3 scripts/migrate-db.py
    
    if [ $? -eq 0 ]; then
        log_success "Database initialization completed"
    else
        log_error "Database initialization failed"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p /app/logs
    mkdir -p /app/uploads
    mkdir -p /app/data
    mkdir -p /app/backups
    
    # Set proper permissions
    chown -R www-data:www-data /app/logs /app/uploads /app/data /app/backups
    
    log_success "Directories created and permissions set"
}

# Start backend service
start_backend() {
    log "Starting backend service..."
    
    cd /app/backend
    
    # Set Python path
    export PYTHONPATH="/app/backend/src"
    
    # Start with gunicorn for production
    if command -v gunicorn &> /dev/null; then
        gunicorn \
            --bind 0.0.0.0:5000 \
            --workers ${WORKERS:-4} \
            --threads ${THREADS:-2} \
            --timeout ${TIMEOUT:-300} \
            --worker-class gevent \
            --worker-connections 1000 \
            --max-requests 1000 \
            --max-requests-jitter 50 \
            --preload \
            --access-logfile /app/logs/access.log \
            --error-logfile /app/logs/error.log \
            --log-level info \
            --daemon \
            --pid /app/logs/backend.pid \
            src.main:app
    else
        # Fallback to Flask development server
        log_warning "Gunicorn not available, using Flask development server"
        python3 src/main.py &
        echo $! > /app/logs/backend.pid
    fi
    
    log_success "Backend service started"
}

# Start frontend service
start_frontend() {
    log "Starting frontend service..."
    
    cd /app/frontend
    
    # Check if build directory exists
    if [ ! -d "build" ]; then
        log "Building frontend..."
        npm run build
    fi
    
    # Start with serve for production
    if command -v serve &> /dev/null; then
        serve \
            -s build \
            -l 3000 \
            -n \
            --cors \
            --no-clipboard \
            --silent > /app/logs/frontend.log 2>&1 &
        echo $! > /app/logs/frontend.pid
    else
        # Fallback to simple HTTP server
        log_warning "serve not available, using simple HTTP server"
        cd build
        python3 -m http.server 3000 > /app/logs/frontend.log 2>&1 &
        echo $! > /app/logs/frontend.pid
    fi
    
    log_success "Frontend service started"
}

# Start with PM2 (if available)
start_with_pm2() {
    log "Starting services with PM2..."
    
    # Install serve globally if not available
    if ! command -v serve &> /dev/null; then
        npm install -g serve
    fi
    
    # Start PM2 services
    pm2 start /app/config/ecosystem.config.js --env production --no-daemon
}

# Health check function
health_check() {
    log "Running health checks..."
    
    # Check backend
    for i in {1..30}; do
        if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
            log_success "Backend health check passed"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "Backend health check failed"
            return 1
        fi
        
        log "Backend not ready, waiting... ($i/30)"
        sleep 2
    done
    
    # Check frontend
    for i in {1..30}; do
        if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
            log_success "Frontend health check passed"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "Frontend health check failed"
            return 1
        fi
        
        log "Frontend not ready, waiting... ($i/30)"
        sleep 2
    done
    
    log_success "All health checks passed"
}

# Cleanup function for graceful shutdown
cleanup() {
    log "Shutting down services..."
    
    # Stop PM2 if running
    if command -v pm2 &> /dev/null && pm2 list | grep -q "online"; then
        pm2 stop all
        pm2 delete all
    fi
    
    # Stop backend
    if [ -f /app/logs/backend.pid ]; then
        PID=$(cat /app/logs/backend.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            log "Backend service stopped"
        fi
    fi
    
    # Stop frontend
    if [ -f /app/logs/frontend.pid ]; then
        PID=$(cat /app/logs/frontend.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            log "Frontend service stopped"
        fi
    fi
    
    log "Cleanup completed"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGTERM SIGINT

# Main function
main() {
    log "Starting BaiKaoTong AI Writing Platform in production mode"
    
    # Create directories
    create_directories
    
    # Wait for external services
    wait_for_db
    
    # Initialize database
    init_database
    
    # Start services
    if command -v pm2 &> /dev/null; then
        start_with_pm2
    else
        start_backend
        sleep 5
        start_frontend
        
        # Run health checks
        health_check
        
        # Keep the script running
        log_success "Services started successfully"
        log "Application is running. Press Ctrl+C to stop."
        
        # Wait for signals
        while true; do
            sleep 30
            
            # Check if services are still running
            if [ -f /app/logs/backend.pid ]; then
                PID=$(cat /app/logs/backend.pid)
                if ! kill -0 $PID 2>/dev/null; then
                    log_error "Backend service stopped unexpectedly"
                    exit 1
                fi
            fi
            
            if [ -f /app/logs/frontend.pid ]; then
                PID=$(cat /app/logs/frontend.pid)
                if ! kill -0 $PID 2>/dev/null; then
                    log_error "Frontend service stopped unexpectedly"
                    exit 1
                fi
            fi
        done
    fi
}

# Run main function
main "$@"
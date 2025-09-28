#!/bin/bash

# BaiKaoTong AI Writing Platform - Update Script
# This script handles updates for both local and production deployments

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
BACKUP_DIR="$BASE_DIR/backups"
UPDATE_LOG="$BASE_DIR/logs/update.log"
VERSION_FILE="$BASE_DIR/VERSION"

# Default values
BACKUP_ENABLED=true
SKIP_TESTS=false
FORCE_UPDATE=false
UPDATE_METHOD=""

# Logging function
log() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo -e "${BLUE}${message}${NC}"
    echo "$message" >> "$UPDATE_LOG"
}

log_success() {
    local message="[SUCCESS] $1"
    echo -e "${GREEN}${message}${NC}"
    echo "$message" >> "$UPDATE_LOG"
}

log_warning() {
    local message="[WARNING] $1"
    echo -e "${YELLOW}${message}${NC}"
    echo "$message" >> "$UPDATE_LOG"
}

log_error() {
    local message="[ERROR] $1"
    echo -e "${RED}${message}${NC}"
    echo "$message" >> "$UPDATE_LOG"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --method [docker|pm2|auto]  Update method (default: auto)"
    echo "  -b, --branch BRANCH             Git branch to update to (default: main)"
    echo "  --skip-backup                   Skip backup creation"
    echo "  --skip-tests                    Skip running tests"
    echo "  --force                         Force update even if no changes"
    echo "  -h, --help                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                              Auto-detect and update"
    echo "  $0 --method docker              Update Docker deployment"
    echo "  $0 --method pm2 --branch develop  Update PM2 deployment from develop branch"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--method)
                UPDATE_METHOD="$2"
                shift 2
                ;;
            -b|--branch)
                GIT_BRANCH="$2"
                shift 2
                ;;
            --skip-backup)
                BACKUP_ENABLED=false
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --force)
                FORCE_UPDATE=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Set defaults
    GIT_BRANCH=${GIT_BRANCH:-"main"}
}

# Detect deployment method
detect_deployment_method() {
    if [ -n "$UPDATE_METHOD" ] && [ "$UPDATE_METHOD" != "auto" ]; then
        log "Using specified update method: $UPDATE_METHOD"
        return
    fi
    
    log "Auto-detecting deployment method..."
    
    # Check for Docker
    if [ -f "$BASE_DIR/deployment/docker/docker-compose.yml" ] && command -v docker &> /dev/null; then
        if docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" ps | grep -q "Up"; then
            UPDATE_METHOD="docker"
            log "Detected Docker deployment"
            return
        fi
    fi
    
    # Check for PM2
    if command -v pm2 &> /dev/null; then
        if pm2 list | grep -q "online"; then
            UPDATE_METHOD="pm2"
            log "Detected PM2 deployment"
            return
        fi
    fi
    
    # Default to pm2 if nothing detected
    UPDATE_METHOD="pm2"
    log_warning "Could not detect deployment method, defaulting to PM2"
}

# Create backup
create_backup() {
    if [ "$BACKUP_ENABLED" = false ]; then
        log_warning "Backup skipped"
        return
    fi
    
    log "Creating backup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Get current version
    CURRENT_VERSION=""
    if [ -f "$VERSION_FILE" ]; then
        CURRENT_VERSION=$(cat "$VERSION_FILE")
    fi
    
    # Create backup filename
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_NAME="backup_${CURRENT_VERSION}_${BACKUP_TIMESTAMP}"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    # Create backup directory
    mkdir -p "$BACKUP_PATH"
    
    # Backup application files
    log "Backing up application files..."
    rsync -av --exclude='.git' --exclude='node_modules' --exclude='venv' \
          --exclude='logs' --exclude='backups' --exclude='uploads' \
          "$BASE_DIR/" "$BACKUP_PATH/app/"
    
    # Backup database (if PostgreSQL)
    if [ "$UPDATE_METHOD" = "docker" ] || command -v pg_dump &> /dev/null; then
        log "Backing up database..."
        
        if [ -f "$BASE_DIR/.env" ]; then
            source "$BASE_DIR/.env"
        fi
        
        if [ "$DB_TYPE" = "postgresql" ] && [ -n "$DB_NAME" ]; then
            if [ "$UPDATE_METHOD" = "docker" ]; then
                # Backup from Docker container
                docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" \
                    exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_PATH/database.sql"
            else
                # Direct backup
                PGPASSWORD="$DB_PASSWORD" pg_dump -h "${DB_HOST:-localhost}" -U "$DB_USER" "$DB_NAME" > "$BACKUP_PATH/database.sql"
            fi
            log_success "Database backup created"
        elif [ "$DB_TYPE" = "sqlite" ] && [ -f "$DB_PATH" ]; then
            cp "$DB_PATH" "$BACKUP_PATH/database.sqlite"
            log_success "SQLite database backup created"
        fi
    fi
    
    # Create backup manifest
    cat > "$BACKUP_PATH/manifest.txt" << EOF
Backup created: $(date)
Previous version: $CURRENT_VERSION
Git branch: $GIT_BRANCH
Deployment method: $UPDATE_METHOD
EOF
    
    # Compress backup
    log "Compressing backup..."
    cd "$BACKUP_DIR"
    tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME/"
    rm -rf "$BACKUP_NAME/"
    
    log_success "Backup created: $BACKUP_NAME.tar.gz"
    
    # Cleanup old backups (keep last 10)
    ls -t *.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm -f
}

# Check for updates
check_for_updates() {
    log "Checking for updates..."
    
    cd "$BASE_DIR"
    
    # Fetch latest changes
    git fetch origin "$GIT_BRANCH"
    
    # Check if there are updates
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse "origin/$GIT_BRANCH")
    
    if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ] && [ "$FORCE_UPDATE" = false ]; then
        log_success "Already up to date"
        exit 0
    fi
    
    # Show update information
    log "Updates available:"
    git log --oneline "$LOCAL_COMMIT".."$REMOTE_COMMIT"
}

# Pull latest changes
pull_changes() {
    log "Pulling latest changes..."
    
    cd "$BASE_DIR"
    
    # Pull changes
    git pull origin "$GIT_BRANCH"
    
    # Update version file
    NEW_VERSION=$(git rev-parse --short HEAD)
    echo "$NEW_VERSION" > "$VERSION_FILE"
    
    log_success "Code updated to version $NEW_VERSION"
}

# Update dependencies
update_dependencies() {
    log "Updating dependencies..."
    
    # Update backend dependencies
    if [ -f "$BASE_DIR/backend/requirements.txt" ]; then
        log "Updating Python dependencies..."
        
        if [ "$UPDATE_METHOD" = "docker" ]; then
            # Dependencies will be updated during Docker build
            log "Python dependencies will be updated during Docker build"
        else
            cd "$BASE_DIR/backend"
            if [ -d "venv" ]; then
                source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                deactivate
            else
                pip3 install --upgrade pip
                pip3 install -r requirements.txt
            fi
            log_success "Python dependencies updated"
        fi
    fi
    
    # Update frontend dependencies
    if [ -f "$BASE_DIR/frontend/package.json" ]; then
        log "Updating Node.js dependencies..."
        
        cd "$BASE_DIR/frontend"
        npm ci
        
        if [ "$UPDATE_METHOD" != "docker" ]; then
            log "Building frontend..."
            npm run build
        fi
        
        log_success "Node.js dependencies updated"
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd "$BASE_DIR"
    
    if [ "$UPDATE_METHOD" = "docker" ]; then
        # Migrations will run automatically in Docker container
        log "Database migrations will run automatically in Docker container"
    else
        # Run migrations directly
        if [ -f "deployment/scripts/migrate-db.py" ]; then
            python3 deployment/scripts/migrate-db.py
            log_success "Database migrations completed"
        else
            log_warning "Migration script not found, skipping"
        fi
    fi
}

# Run tests
run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "Tests skipped"
        return
    fi
    
    log "Running tests..."
    
    # Backend tests
    if [ -f "$BASE_DIR/backend/test_requirements.txt" ]; then
        cd "$BASE_DIR/backend"
        if [ -d "venv" ]; then
            source venv/bin/activate
            pip install -r test_requirements.txt
            python -m pytest tests/ -v
            deactivate
        else
            pip3 install pytest
            python3 -m pytest tests/ -v
        fi
        log_success "Backend tests passed"
    fi
    
    # Frontend tests
    if [ -f "$BASE_DIR/frontend/package.json" ] && grep -q "test" "$BASE_DIR/frontend/package.json"; then
        cd "$BASE_DIR/frontend"
        npm test -- --coverage --watchAll=false
        log_success "Frontend tests passed"
    fi
}

# Restart services
restart_services() {
    log "Restarting services..."
    
    if [ "$UPDATE_METHOD" = "docker" ]; then
        # Docker update
        cd "$BASE_DIR/deployment/docker"
        
        log "Rebuilding and restarting Docker containers..."
        docker-compose build --no-cache
        docker-compose up -d --force-recreate
        
        # Wait for services to be ready
        log "Waiting for services to be ready..."
        sleep 30
        
        # Health check
        if docker-compose ps | grep -q "Up"; then
            log_success "Docker services restarted successfully"
        else
            log_error "Docker services failed to start"
            exit 1
        fi
        
    elif [ "$UPDATE_METHOD" = "pm2" ]; then
        # PM2 update
        if command -v pm2 &> /dev/null && pm2 list | grep -q "online"; then
            log "Restarting PM2 services..."
            pm2 reload all --update-env
            pm2 save
            
            # Wait for services
            sleep 10
            
            if pm2 list | grep -q "online"; then
                log_success "PM2 services restarted successfully"
            else
                log_error "PM2 services failed to start"
                exit 1
            fi
        else
            log_warning "PM2 services not running, please start them manually"
        fi
    fi
}

# Cleanup function
cleanup_after_update() {
    log "Running post-update cleanup..."
    
    # Clear temporary files
    find "$BASE_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$BASE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Clear npm cache
    if command -v npm &> /dev/null; then
        npm cache clean --force 2>/dev/null || true
    fi
    
    log_success "Cleanup completed"
}

# Main update function
main() {
    log "Starting update process for $PROJECT_NAME"
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$UPDATE_LOG")"
    
    # Create backup
    create_backup
    
    # Check for updates
    check_for_updates
    
    # Pull latest changes
    pull_changes
    
    # Update dependencies
    update_dependencies
    
    # Run database migrations
    run_migrations
    
    # Run tests
    run_tests
    
    # Restart services
    restart_services
    
    # Cleanup
    cleanup_after_update
    
    # Final health check
    log "Running final health check..."
    sleep 10
    
    # Check if services are responding
    if curl -f -s http://localhost:3000 > /dev/null 2>&1 && \
       curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
        log_success "🎉 Update completed successfully!"
        log "Application is running and responding to health checks"
    else
        log_warning "Update completed but services may not be fully ready yet"
        log "Please check the service logs if issues persist"
    fi
}

# Handle script interruption
cleanup() {
    log_warning "Update interrupted"
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Parse arguments and run main function
parse_args "$@"
detect_deployment_method
main
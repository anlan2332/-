#!/bin/bash

# BaiKaoTong AI Writing Platform - Maintenance Script
# This script handles various maintenance tasks

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
LOG_DIR="$BASE_DIR/logs"
UPLOAD_DIR="$BASE_DIR/uploads"

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

# Show usage
show_usage() {
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  backup           Create a full system backup"
    echo "  restore          Restore from a backup"
    echo "  cleanup          Clean up temporary files and logs"
    echo "  health           Run health checks"
    echo "  logs             View application logs"
    echo "  status           Show service status"
    echo "  restart          Restart services"
    echo "  reset            Reset application (WARNING: destructive)"
    echo ""
    echo "Options:"
    echo "  --backup-file FILE    Backup file for restore command"
    echo "  --days N              Number of days for log retention (default: 30)"
    echo "  --follow              Follow log output"
    echo "  --service NAME        Specific service for logs/restart"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 backup                     Create backup"
    echo "  $0 restore --backup-file backup.tar.gz"
    echo "  $0 cleanup --days 7           Clean files older than 7 days"
    echo "  $0 logs --follow              Follow live logs"
    echo "  $0 restart --service backend  Restart only backend"
}

# Detect deployment method
detect_deployment_method() {
    if [ -f "$BASE_DIR/deployment/docker/docker-compose.yml" ] && command -v docker &> /dev/null; then
        if docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" ps | grep -q "Up"; then
            echo "docker"
            return
        fi
    fi
    
    if command -v pm2 &> /dev/null && pm2 list | grep -q "online"; then
        echo "pm2"
        return
    fi
    
    echo "unknown"
}

# Create backup
create_backup() {
    log "Creating full system backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_NAME="full_backup_$BACKUP_TIMESTAMP"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup application files
    log "Backing up application files..."
    rsync -av --exclude='.git' --exclude='node_modules' --exclude='venv' \
          --exclude='logs' --exclude='backups' \
          "$BASE_DIR/" "$BACKUP_PATH/app/"
    
    # Backup database
    log "Backing up database..."
    DEPLOYMENT_METHOD=$(detect_deployment_method)
    
    if [ -f "$BASE_DIR/.env" ]; then
        source "$BASE_DIR/.env"
    fi
    
    if [ "$DB_TYPE" = "postgresql" ]; then
        if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
            docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" \
                exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_PATH/database.sql"
        else
            PGPASSWORD="$DB_PASSWORD" pg_dump -h "${DB_HOST:-localhost}" -U "$DB_USER" "$DB_NAME" > "$BACKUP_PATH/database.sql"
        fi
    elif [ "$DB_TYPE" = "sqlite" ] && [ -f "$DB_PATH" ]; then
        cp "$DB_PATH" "$BACKUP_PATH/database.sqlite"
    fi
    
    # Backup uploads
    if [ -d "$UPLOAD_DIR" ]; then
        log "Backing up uploaded files..."
        rsync -av "$UPLOAD_DIR/" "$BACKUP_PATH/uploads/"
    fi
    
    # Create backup manifest
    cat > "$BACKUP_PATH/manifest.txt" << EOF
Backup Type: Full System Backup
Created: $(date)
Git Commit: $(cd "$BASE_DIR" && git rev-parse HEAD 2>/dev/null || echo "Unknown")
Deployment Method: $DEPLOYMENT_METHOD
Database Type: ${DB_TYPE:-unknown}
Files Included:
- Application code
- Database dump
- Uploaded files
- Configuration files
EOF
    
    # Compress backup
    log "Compressing backup..."
    cd "$BACKUP_DIR"
    tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME/"
    rm -rf "$BACKUP_NAME/"
    
    log_success "Backup created: $BACKUP_NAME.tar.gz"
    
    # Show backup size
    BACKUP_SIZE=$(du -h "$BACKUP_NAME.tar.gz" | cut -f1)
    log "Backup size: $BACKUP_SIZE"
}

# Restore from backup
restore_backup() {
    if [ -z "$BACKUP_FILE" ]; then
        log_error "Backup file not specified. Use --backup-file option."
        exit 1
    fi
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    log_warning "This will restore the system from backup and overwrite current data."
    read -p "Are you sure you want to continue? (y/N): " confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        log "Restore cancelled."
        exit 0
    fi
    
    log "Restoring from backup: $BACKUP_FILE"
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Extract backup
    log "Extracting backup..."
    tar -xzf "$BACKUP_FILE"
    
    EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "*backup*" | head -1)
    if [ -z "$EXTRACTED_DIR" ]; then
        log_error "Invalid backup file format"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    # Stop services
    log "Stopping services..."
    DEPLOYMENT_METHOD=$(detect_deployment_method)
    
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" down
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        pm2 stop all || true
    fi
    
    # Restore application files
    log "Restoring application files..."
    rsync -av --delete "$EXTRACTED_DIR/app/" "$BASE_DIR/"
    
    # Restore database
    if [ -f "$EXTRACTED_DIR/database.sql" ]; then
        log "Restoring PostgreSQL database..."
        source "$BASE_DIR/.env"
        
        if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
            # Start only database for restore
            docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" up -d postgres
            sleep 10
            
            # Drop and recreate database
            docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" \
                exec -T postgres psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;"
            docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" \
                exec -T postgres psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"
            
            # Restore data
            docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" \
                exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" < "$EXTRACTED_DIR/database.sql"
        else
            # Direct restore
            PGPASSWORD="$DB_PASSWORD" psql -h "${DB_HOST:-localhost}" -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;"
            PGPASSWORD="$DB_PASSWORD" psql -h "${DB_HOST:-localhost}" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"
            PGPASSWORD="$DB_PASSWORD" psql -h "${DB_HOST:-localhost}" -U "$DB_USER" -d "$DB_NAME" < "$EXTRACTED_DIR/database.sql"
        fi
    elif [ -f "$EXTRACTED_DIR/database.sqlite" ]; then
        log "Restoring SQLite database..."
        cp "$EXTRACTED_DIR/database.sqlite" "$DB_PATH"
    fi
    
    # Restore uploads
    if [ -d "$EXTRACTED_DIR/uploads" ]; then
        log "Restoring uploaded files..."
        mkdir -p "$UPLOAD_DIR"
        rsync -av "$EXTRACTED_DIR/uploads/" "$UPLOAD_DIR/"
    fi
    
    # Restart services
    log "Restarting services..."
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" up -d
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        cd "$BASE_DIR"
        pm2 start deployment/config/ecosystem.config.js --env production
    fi
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    log_success "Restore completed successfully!"
}

# Cleanup old files and logs
cleanup_system() {
    RETENTION_DAYS=${RETENTION_DAYS:-30}
    
    log "Cleaning up system (keeping last $RETENTION_DAYS days)..."
    
    # Clean old log files
    if [ -d "$LOG_DIR" ]; then
        log "Cleaning old log files..."
        find "$LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
        find "$LOG_DIR" -name "*.log.*" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    fi
    
    # Clean old backups
    if [ -d "$BACKUP_DIR" ]; then
        log "Cleaning old backups..."
        find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    fi
    
    # Clean temporary files
    log "Cleaning temporary files..."
    find "$BASE_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$BASE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BASE_DIR" -name ".DS_Store" -delete 2>/dev/null || true
    find "$BASE_DIR" -name "Thumbs.db" -delete 2>/dev/null || true
    
    # Clean npm cache
    if command -v npm &> /dev/null; then
        npm cache clean --force 2>/dev/null || true
    fi
    
    # Clean pip cache
    if command -v pip &> /dev/null; then
        pip cache purge 2>/dev/null || true
    elif command -v pip3 &> /dev/null; then
        pip3 cache purge 2>/dev/null || true
    fi
    
    # Rotate large log files
    if [ -d "$LOG_DIR" ]; then
        for logfile in "$LOG_DIR"/*.log; do
            if [ -f "$logfile" ] && [ $(stat -f%z "$logfile" 2>/dev/null || stat -c%s "$logfile" 2>/dev/null || echo 0) -gt 104857600 ]; then  # 100MB
                log "Rotating large log file: $(basename "$logfile")"
                mv "$logfile" "$logfile.$(date +%Y%m%d_%H%M%S)"
                touch "$logfile"
            fi
        done
    fi
    
    log_success "System cleanup completed"
}

# Health check
run_health_check() {
    log "Running health checks..."
    
    local errors=0
    
    # Check disk space
    log "Checking disk space..."
    DISK_USAGE=$(df "$BASE_DIR" | awk 'NR==2{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        log_error "Disk usage is high: ${DISK_USAGE}%"
        errors=$((errors + 1))
    else
        log_success "Disk usage OK: ${DISK_USAGE}%"
    fi
    
    # Check memory usage
    log "Checking memory usage..."
    if command -v free &> /dev/null; then
        MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [ "$MEM_USAGE" -gt 90 ]; then
            log_error "Memory usage is high: ${MEM_USAGE}%"
            errors=$((errors + 1))
        else
            log_success "Memory usage OK: ${MEM_USAGE}%"
        fi
    fi
    
    # Check services
    log "Checking services..."
    DEPLOYMENT_METHOD=$(detect_deployment_method)
    
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        if docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" ps | grep -q "Up"; then
            log_success "Docker services are running"
        else
            log_error "Some Docker services are not running"
            errors=$((errors + 1))
        fi
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        if pm2 list | grep -q "online"; then
            log_success "PM2 services are running"
        else
            log_error "PM2 services are not running"
            errors=$((errors + 1))
        fi
    else
        log_warning "Could not detect running services"
    fi
    
    # Check HTTP endpoints
    log "Checking HTTP endpoints..."
    
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend is responding"
    else
        log_error "Frontend is not responding"
        errors=$((errors + 1))
    fi
    
    if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
        log_success "Backend is responding"
    else
        log_error "Backend is not responding"
        errors=$((errors + 1))
    fi
    
    # Summary
    if [ $errors -eq 0 ]; then
        log_success "All health checks passed"
    else
        log_error "$errors health check(s) failed"
    fi
    
    return $errors
}

# View logs
view_logs() {
    DEPLOYMENT_METHOD=$(detect_deployment_method)
    
    if [ -n "$SERVICE_NAME" ]; then
        log "Viewing logs for service: $SERVICE_NAME"
    else
        log "Viewing application logs"
    fi
    
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        if [ "$FOLLOW_LOGS" = true ]; then
            if [ -n "$SERVICE_NAME" ]; then
                docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" logs -f "$SERVICE_NAME"
            else
                docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" logs -f
            fi
        else
            if [ -n "$SERVICE_NAME" ]; then
                docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" logs --tail=100 "$SERVICE_NAME"
            else
                docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" logs --tail=100
            fi
        fi
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        if [ "$FOLLOW_LOGS" = true ]; then
            if [ -n "$SERVICE_NAME" ]; then
                pm2 logs "$SERVICE_NAME"
            else
                pm2 logs
            fi
        else
            if [ -n "$SERVICE_NAME" ]; then
                pm2 logs "$SERVICE_NAME" --nostream --lines 100
            else
                pm2 logs --nostream --lines 100
            fi
        fi
    else
        # View log files directly
        if [ -d "$LOG_DIR" ]; then
            if [ "$FOLLOW_LOGS" = true ]; then
                tail -f "$LOG_DIR"/*.log
            else
                tail -100 "$LOG_DIR"/*.log
            fi
        else
            log_error "Log directory not found: $LOG_DIR"
        fi
    fi
}

# Show service status
show_status() {
    log "Service Status:"
    
    DEPLOYMENT_METHOD=$(detect_deployment_method)
    
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" ps
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        pm2 status
    else
        log_warning "No services detected"
    fi
    
    # Show resource usage
    echo ""
    log "System Resources:"
    
    # Disk usage
    df -h "$BASE_DIR" | awk 'NR==2{print "Disk Usage: "$5" of "$2" used"}'
    
    # Memory usage
    if command -v free &> /dev/null; then
        free -h | awk 'NR==2{print "Memory Usage: "$3" of "$2" used"}'
    fi
    
    # Load average
    if [ -f /proc/loadavg ]; then
        echo "Load Average: $(cat /proc/loadavg | cut -d' ' -f1-3)"
    fi
}

# Restart services
restart_services() {
    DEPLOYMENT_METHOD=$(detect_deployment_method)
    
    if [ -n "$SERVICE_NAME" ]; then
        log "Restarting service: $SERVICE_NAME"
    else
        log "Restarting all services"
    fi
    
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        if [ -n "$SERVICE_NAME" ]; then
            docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" restart "$SERVICE_NAME"
        else
            docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" restart
        fi
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        if [ -n "$SERVICE_NAME" ]; then
            pm2 restart "$SERVICE_NAME"
        else
            pm2 restart all
        fi
    else
        log_error "No running services detected to restart"
        exit 1
    fi
    
    log_success "Services restarted successfully"
}

# Reset application (WARNING: destructive)
reset_application() {
    log_warning "This will completely reset the application and delete all data!"
    log_warning "This includes:"
    log_warning "  - Database content"
    log_warning "  - Uploaded files"
    log_warning "  - Log files"
    log_warning "  - User accounts"
    
    read -p "Type 'RESET' to confirm this destructive action: " confirm
    
    if [ "$confirm" != "RESET" ]; then
        log "Reset cancelled."
        exit 0
    fi
    
    log "Resetting application..."
    
    DEPLOYMENT_METHOD=$(detect_deployment_method)
    
    # Stop services
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" down -v
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        pm2 stop all || true
        pm2 delete all || true
    fi
    
    # Remove data
    log "Removing application data..."
    rm -rf "$BASE_DIR/data"
    rm -rf "$BASE_DIR/logs"
    rm -rf "$BASE_DIR/uploads"
    rm -rf "$BASE_DIR/backups"
    
    # Recreate directories
    mkdir -p "$BASE_DIR/data"
    mkdir -p "$BASE_DIR/logs"
    mkdir -p "$BASE_DIR/uploads"
    mkdir -p "$BASE_DIR/backups"
    
    # Reset database
    if [ -f "$BASE_DIR/.env" ]; then
        source "$BASE_DIR/.env"
        
        if [ "$DB_TYPE" = "sqlite" ]; then
            rm -f "$DB_PATH"
        fi
    fi
    
    # Restart services
    log "Restarting services..."
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        docker-compose -f "$BASE_DIR/deployment/docker/docker-compose.yml" up -d
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        cd "$BASE_DIR"
        pm2 start deployment/config/ecosystem.config.js --env production
    fi
    
    log_success "Application reset completed"
}

# Parse arguments
parse_args() {
    COMMAND=""
    BACKUP_FILE=""
    RETENTION_DAYS=30
    FOLLOW_LOGS=false
    SERVICE_NAME=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            backup|restore|cleanup|health|logs|status|restart|reset)
                if [ -z "$COMMAND" ]; then
                    COMMAND="$1"
                else
                    log_error "Multiple commands specified"
                    exit 1
                fi
                shift
                ;;
            --backup-file)
                BACKUP_FILE="$2"
                shift 2
                ;;
            --days)
                RETENTION_DAYS="$2"
                shift 2
                ;;
            --follow)
                FOLLOW_LOGS=true
                shift
                ;;
            --service)
                SERVICE_NAME="$2"
                shift 2
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
    
    if [ -z "$COMMAND" ]; then
        log_error "No command specified"
        show_usage
        exit 1
    fi
}

# Main function
main() {
    log "BaiKaoTong AI Writing Platform - Maintenance Tool"
    
    case $COMMAND in
        backup)
            create_backup
            ;;
        restore)
            restore_backup
            ;;
        cleanup)
            cleanup_system
            ;;
        health)
            run_health_check
            ;;
        logs)
            view_logs
            ;;
        status)
            show_status
            ;;
        restart)
            restart_services
            ;;
        reset)
            reset_application
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
}

# Parse arguments and run
parse_args "$@"
main
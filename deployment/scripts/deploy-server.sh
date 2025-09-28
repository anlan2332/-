#!/bin/bash

# BaiKaoTong AI Writing Platform - Server Deployment Script
# This script sets up the platform for production server deployment

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
DOCKER_DIR="$DEPLOYMENT_DIR/docker"

# Default deployment method
DEPLOYMENT_METHOD="docker"  # docker or pm2

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
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --method [docker|pm2]  Deployment method (default: docker)"
    echo "  -d, --domain DOMAIN        Domain name for the deployment"
    echo "  -p, --port PORT           HTTP port (default: 80)"
    echo "  --ssl                     Enable SSL/TLS"
    echo "  --ssl-cert PATH           Path to SSL certificate"
    echo "  --ssl-key PATH            Path to SSL private key"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --method docker --domain example.com --ssl"
    echo "  $0 --method pm2 --domain example.com --port 8080"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--method)
                DEPLOYMENT_METHOD="$2"
                shift 2
                ;;
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -p|--port)
                HTTP_PORT="$2"
                shift 2
                ;;
            --ssl)
                SSL_ENABLED=true
                shift
                ;;
            --ssl-cert)
                SSL_CERT_PATH="$2"
                shift 2
                ;;
            --ssl-key)
                SSL_KEY_PATH="$2"
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
    
    # Set defaults
    HTTP_PORT=${HTTP_PORT:-80}
    DOMAIN=${DOMAIN:-"localhost"}
    SSL_ENABLED=${SSL_ENABLED:-false}
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        # Check Docker
        if ! command -v docker &> /dev/null; then
            log_error "Docker is not installed. Please install Docker."
            exit 1
        fi
        
        # Check Docker Compose
        if ! command -v docker-compose &> /dev/null; then
            log_error "Docker Compose is not installed. Please install Docker Compose."
            exit 1
        fi
        
        # Check Docker service
        if ! systemctl is-active --quiet docker; then
            log_warning "Docker service is not running. Starting Docker..."
            sudo systemctl start docker
        fi
        
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        # Check Node.js
        if ! command -v node &> /dev/null; then
            log_error "Node.js is not installed. Please install Node.js 16 or higher."
            exit 1
        fi
        
        # Check Python
        if ! command -v python3 &> /dev/null; then
            log_error "Python 3 is not installed. Please install Python 3.8 or higher."
            exit 1
        fi
        
        # Check PostgreSQL (for PM2 deployment)
        if ! command -v psql &> /dev/null; then
            log_warning "PostgreSQL client not found. Installing..."
            sudo apt-get update
            sudo apt-get install -y postgresql-client
        fi
    fi
    
    log_success "System requirements check passed"
}

# Setup environment
setup_environment() {
    log "Setting up production environment..."
    
    # Create production environment file
    if [ ! -f "$BASE_DIR/.env" ]; then
        cp "$CONFIG_DIR/.env.production" "$BASE_DIR/.env"
        log_success "Production environment configuration copied"
        
        # Update domain in environment
        if [ -n "$DOMAIN" ]; then
            sed -i "s/yourdomain.com/$DOMAIN/g" "$BASE_DIR/.env"
        fi
        
        log_warning "Please update the .env file with your production configuration:"
        log_warning "  - DOUBAO_API_KEY: Your Doubao AI API key"
        log_warning "  - SECRET_KEY: A secure secret key"
        log_warning "  - DB_PASSWORD: Secure database password"
        log_warning "  - Other production settings"
        
        read -p "Press Enter after updating the configuration file..."
    fi
}

# Docker deployment
deploy_with_docker() {
    log "Deploying with Docker..."
    
    cd "$DOCKER_DIR"
    
    # Build and start services
    log "Building Docker images..."
    docker-compose build --no-cache
    
    log "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "Up"; then
        log_success "Services started successfully"
    else
        log_error "Some services failed to start"
        docker-compose logs
        exit 1
    fi
    
    # Show running services
    docker-compose ps
}

# PM2 deployment
deploy_with_pm2() {
    log "Deploying with PM2..."
    
    # Install dependencies
    log "Installing dependencies..."
    
    # Backend
    cd "$BASE_DIR/backend"
    python3 -m pip install --upgrade pip
    pip3 install -r requirements.txt
    
    # Frontend
    cd "$BASE_DIR/frontend"
    npm ci --production
    npm run build
    
    # Install PM2 if not installed
    if ! command -v pm2 &> /dev/null; then
        npm install -g pm2
    fi
    
    # Initialize database
    cd "$BASE_DIR"
    python3 "$SCRIPTS_DIR/migrate-db.py"
    
    # Start services with PM2
    log "Starting services with PM2..."
    pm2 start "$CONFIG_DIR/ecosystem.config.js" --env production
    
    # Save PM2 configuration
    pm2 save
    
    # Setup PM2 startup
    pm2 startup
    
    log_success "PM2 services started successfully"
}

# Setup SSL/TLS
setup_ssl() {
    if [ "$SSL_ENABLED" = true ]; then
        log "Setting up SSL/TLS..."
        
        # Create SSL directory
        mkdir -p "$BASE_DIR/ssl"
        
        if [ -n "$SSL_CERT_PATH" ] && [ -n "$SSL_KEY_PATH" ]; then
            # Copy provided certificates
            cp "$SSL_CERT_PATH" "$BASE_DIR/ssl/server.crt"
            cp "$SSL_KEY_PATH" "$BASE_DIR/ssl/server.key"
            log_success "SSL certificates copied"
        else
            # Generate self-signed certificate for testing
            log_warning "Generating self-signed SSL certificate for testing..."
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout "$BASE_DIR/ssl/server.key" \
                -out "$BASE_DIR/ssl/server.crt" \
                -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
            log_warning "Self-signed certificate generated. Replace with proper certificate in production."
        fi
    fi
}

# Setup firewall
setup_firewall() {
    log "Setting up firewall rules..."
    
    # Allow SSH (port 22)
    sudo ufw allow 22/tcp
    
    # Allow HTTP (port 80)
    sudo ufw allow 80/tcp
    
    # Allow HTTPS (port 443)
    if [ "$SSL_ENABLED" = true ]; then
        sudo ufw allow 443/tcp
    fi
    
    # Allow custom HTTP port if different from 80
    if [ "$HTTP_PORT" != "80" ]; then
        sudo ufw allow "$HTTP_PORT/tcp"
    fi
    
    # Enable firewall
    sudo ufw --force enable
    
    log_success "Firewall configured"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring and logging..."
    
    # Create log directories
    mkdir -p "$BASE_DIR/logs"
    
    # Setup log rotation
    cat > /tmp/baikao-logrotate << EOF
$BASE_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        if [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
            pm2 reloadLogs
        fi
    endscript
}
EOF
    
    sudo mv /tmp/baikao-logrotate /etc/logrotate.d/baikao
    
    log_success "Monitoring and logging configured"
}

# Main deployment function
main() {
    log "Starting server deployment of $PROJECT_NAME"
    log "Deployment method: $DEPLOYMENT_METHOD"
    log "Domain: $DOMAIN"
    log "Port: $HTTP_PORT"
    log "SSL enabled: $SSL_ENABLED"
    
    check_requirements
    setup_environment
    setup_ssl
    
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        deploy_with_docker
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        deploy_with_pm2
    else
        log_error "Invalid deployment method: $DEPLOYMENT_METHOD"
        exit 1
    fi
    
    setup_firewall
    setup_monitoring
    
    # Show deployment info
    log ""
    log_success "🎉 Server deployment completed successfully!"
    log ""
    log "Access your application at:"
    if [ "$SSL_ENABLED" = true ]; then
        log "  Frontend: ${GREEN}https://$DOMAIN${NC}"
        log "  Backend API: ${GREEN}https://$DOMAIN/api${NC}"
    else
        if [ "$HTTP_PORT" = "80" ]; then
            log "  Frontend: ${GREEN}http://$DOMAIN${NC}"
            log "  Backend API: ${GREEN}http://$DOMAIN/api${NC}"
        else
            log "  Frontend: ${GREEN}http://$DOMAIN:$HTTP_PORT${NC}"
            log "  Backend API: ${GREEN}http://$DOMAIN:$HTTP_PORT/api${NC}"
        fi
    fi
    log ""
    
    if [ "$DEPLOYMENT_METHOD" = "docker" ]; then
        log "Docker management commands:"
        log "  View services: ${YELLOW}docker-compose ps${NC}"
        log "  View logs: ${YELLOW}docker-compose logs${NC}"
        log "  Restart services: ${YELLOW}docker-compose restart${NC}"
        log "  Stop services: ${YELLOW}docker-compose down${NC}"
    elif [ "$DEPLOYMENT_METHOD" = "pm2" ]; then
        log "PM2 management commands:"
        log "  View services: ${YELLOW}pm2 status${NC}"
        log "  View logs: ${YELLOW}pm2 logs${NC}"
        log "  Restart services: ${YELLOW}pm2 restart all${NC}"
        log "  Stop services: ${YELLOW}pm2 stop all${NC}"
    fi
}

# Handle script interruption
cleanup() {
    log_warning "Deployment interrupted"
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Parse arguments and run main function
parse_args "$@"
main
#!/bin/bash

# BaiKaoTong AI Writing Platform - Package Script
# This script creates a deployment package

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="BaiKaoTong AI Writing Platform"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="$BASE_DIR/package"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
VERSION=$(cat "$BASE_DIR/VERSION" 2>/dev/null || echo "unknown")

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

# Create package directory
create_package_dir() {
    log "Creating package directory..."
    
    rm -rf "$PACKAGE_DIR"
    mkdir -p "$PACKAGE_DIR"
    
    log_success "Package directory created: $PACKAGE_DIR"
}

# Copy application files
copy_application() {
    log "Copying application files..."
    
    # Copy main application files
    cp -r "$BASE_DIR"/* "$PACKAGE_DIR/" 2>/dev/null || true
    
    # Remove excluded files and directories
    rm -rf "$PACKAGE_DIR/.git"
    rm -rf "$PACKAGE_DIR/node_modules"
    rm -rf "$PACKAGE_DIR"/*/node_modules
    rm -rf "$PACKAGE_DIR/venv"
    rm -rf "$PACKAGE_DIR"/*/venv
    find "$PACKAGE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PACKAGE_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$PACKAGE_DIR" -name ".DS_Store" -delete 2>/dev/null || true
    find "$PACKAGE_DIR" -name "Thumbs.db" -delete 2>/dev/null || true
    rm -rf "$PACKAGE_DIR/logs"
    rm -rf "$PACKAGE_DIR/data"
    rm -rf "$PACKAGE_DIR/uploads"
    rm -rf "$PACKAGE_DIR/backups"
    rm -rf "$PACKAGE_DIR/package"
    rm -f "$PACKAGE_DIR/.env"
    rm -f "$PACKAGE_DIR/cookies.txt"
    rm -f "$PACKAGE_DIR"/pasted_*
    rm -f "$PACKAGE_DIR"/*.png
    
    log_success "Application files copied"
}

# Create installation script
create_installer() {
    log "Creating installation script..."
    
    cat > "$PACKAGE_DIR/install.sh" << 'EOF'
#!/bin/bash

# BaiKaoTong AI Writing Platform - Installation Script

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --local           Install for local development"
    echo "  --server          Install for production server"
    echo "  --docker          Use Docker deployment (default for server)"
    echo "  --pm2             Use PM2 deployment"
    echo "  --domain DOMAIN   Domain name for server deployment"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --local                      # Local development setup"
    echo "  $0 --server --domain example.com # Server deployment with Docker"
    echo "  $0 --server --pm2 --domain example.com # Server deployment with PM2"
}

# Parse arguments
DEPLOYMENT_TYPE=""
DEPLOYMENT_METHOD=""
DOMAIN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --local)
            DEPLOYMENT_TYPE="local"
            shift
            ;;
        --server)
            DEPLOYMENT_TYPE="server"
            DEPLOYMENT_METHOD="docker"
            shift
            ;;
        --docker)
            DEPLOYMENT_METHOD="docker"
            shift
            ;;
        --pm2)
            DEPLOYMENT_METHOD="pm2"
            shift
            ;;
        --domain)
            DOMAIN="$2"
            shift 2
            ;;
        --help)
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

# Default to local if no type specified
if [ -z "$DEPLOYMENT_TYPE" ]; then
    DEPLOYMENT_TYPE="local"
fi

log "🚀 Installing BaiKaoTong AI Writing Platform"
log "Deployment type: $DEPLOYMENT_TYPE"
log "Deployment method: ${DEPLOYMENT_METHOD:-auto}"
log "Domain: ${DOMAIN:-localhost}"

# Check if we're in the right directory
if [ ! -f "VERSION" ] || [ ! -d "deployment" ]; then
    log_error "Please run this script from the project root directory"
    exit 1
fi

# Make scripts executable
chmod +x deployment/scripts/*.sh
chmod +x deployment/scripts/*.py

if [ "$DEPLOYMENT_TYPE" = "local" ]; then
    log "Starting local deployment..."
    ./deployment/scripts/deploy-local.sh
elif [ "$DEPLOYMENT_TYPE" = "server" ]; then
    log "Starting server deployment..."
    if [ -n "$DOMAIN" ]; then
        ./deployment/scripts/deploy-server.sh --method "$DEPLOYMENT_METHOD" --domain "$DOMAIN"
    else
        ./deployment/scripts/deploy-server.sh --method "$DEPLOYMENT_METHOD"
    fi
fi

log_success "🎉 Installation completed!"

if [ "$DEPLOYMENT_TYPE" = "local" ]; then
    log ""
    log "Access your application at:"
    log "  Frontend: ${GREEN}http://localhost:3000${NC}"
    log "  Backend API: ${GREEN}http://localhost:5000${NC}"
    log ""
    log "Management commands:"
    log "  View status: ${YELLOW}./deployment/scripts/maintenance.sh status${NC}"
    log "  View logs: ${YELLOW}./deployment/scripts/maintenance.sh logs${NC}"
    log "  Update app: ${YELLOW}./deployment/scripts/update.sh${NC}"
else
    log ""
    log "Access your application at:"
    if [ -n "$DOMAIN" ]; then
        log "  Frontend: ${GREEN}http://$DOMAIN${NC}"
        log "  Backend API: ${GREEN}http://$DOMAIN/api${NC}"
    else
        log "  Frontend: ${GREEN}http://your-server-ip${NC}"
        log "  Backend API: ${GREEN}http://your-server-ip/api${NC}"
    fi
    log ""
    log "Management commands:"
    log "  View status: ${YELLOW}./deployment/scripts/maintenance.sh status${NC}"
    log "  View logs: ${YELLOW}./deployment/scripts/maintenance.sh logs${NC}"
    log "  Update app: ${YELLOW}./deployment/scripts/update.sh${NC}"
    log "  Create backup: ${YELLOW}./deployment/scripts/maintenance.sh backup${NC}"
fi

log ""
log "📚 Documentation:"
log "  Main README: ${YELLOW}deployment/docs/README.md${NC}"
log "  Deployment Guide: ${YELLOW}deployment/docs/DEPLOYMENT.md${NC}"
log "  Configuration Guide: ${YELLOW}deployment/docs/CONFIGURATION.md${NC}"
log "  Maintenance Guide: ${YELLOW}deployment/docs/MAINTENANCE.md${NC}"

EOF

    chmod +x "$PACKAGE_DIR/install.sh"
    
    log_success "Installation script created"
}

# Create README for package
create_package_readme() {
    log "Creating package README..."
    
    cat > "$PACKAGE_DIR/README_PACKAGE.md" << EOF
# 百考通AI写作平台 - 部署包

## 快速安装

### 本地开发环境
\`\`\`bash
# 解压到目标目录
tar -xzf baikao-platform-v${VERSION}.tar.gz
cd baikao-platform

# 本地部署
./install.sh --local
\`\`\`

### 生产服务器环境
\`\`\`bash
# 解压到目标目录
tar -xzf baikao-platform-v${VERSION}.tar.gz
cd baikao-platform

# Docker部署（推荐）
./install.sh --server --domain yourdomain.com

# 或PM2部署
./install.sh --server --pm2 --domain yourdomain.com
\`\`\`

## 系统要求

### 本地开发
- Node.js 16+
- Python 3.8+
- Git

### 生产环境
- Docker 20+ & Docker Compose 1.29+（Docker部署）
- 或 Node.js 16+ & Python 3.8+ & PostgreSQL 12+（PM2部署）

## 配置要求

安装后需要配置以下关键参数：

1. 编辑 \`.env\` 文件
2. 设置 \`DOUBAO_API_KEY\`（必需）
3. 设置其他安全密钥

## 文档

详细文档请查看：
- \`deployment/docs/README.md\` - 主要文档
- \`deployment/docs/DEPLOYMENT.md\` - 部署指南
- \`deployment/docs/CONFIGURATION.md\` - 配置说明

## 版本信息

- 版本: ${VERSION}
- 构建时间: ${TIMESTAMP}
- 构建环境: $(uname -a 2>/dev/null || echo "Unknown")

## 技术支持

- 项目文档: deployment/docs/
- 问题反馈: 请联系开发团队
EOF

    log_success "Package README created"
}

# Create compressed package
create_archive() {
    log "Creating compressed package..."
    
    cd "$(dirname "$PACKAGE_DIR")"
    PACKAGE_NAME="baikao-platform-v${VERSION}-${TIMESTAMP}"
    
    # Create tar.gz archive
    tar -czf "${PACKAGE_NAME}.tar.gz" "$(basename "$PACKAGE_DIR")"
    
    # Create zip archive
    if command -v zip &> /dev/null; then
        zip -r "${PACKAGE_NAME}.zip" "$(basename "$PACKAGE_DIR")" >/dev/null
        log_success "ZIP package created: ${PACKAGE_NAME}.zip"
    fi
    
    # Show package info
    ARCHIVE_SIZE=$(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)
    log_success "TAR.GZ package created: ${PACKAGE_NAME}.tar.gz"
    log "Package size: $ARCHIVE_SIZE"
    
    # Create checksums
    if command -v sha256sum &> /dev/null; then
        sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.sha256"
        log_success "Checksum created: ${PACKAGE_NAME}.tar.gz.sha256"
    fi
}

# Cleanup temporary files
cleanup() {
    log "Cleaning up temporary files..."
    rm -rf "$PACKAGE_DIR"
    log_success "Cleanup completed"
}

# Main function
main() {
    log "🎁 Creating deployment package for $PROJECT_NAME"
    log "Version: $VERSION"
    log "Build timestamp: $TIMESTAMP"
    
    create_package_dir
    copy_application
    create_installer
    create_package_readme
    create_archive
    cleanup
    
    log ""
    log_success "🎉 Package creation completed!"
    log ""
    log "📦 Package files:"
    ls -lh baikao-platform-v${VERSION}-${TIMESTAMP}.*
    log ""
    log "📋 Installation instructions:"
    log "1. Transfer the package to your target server"
    log "2. Extract: tar -xzf baikao-platform-v${VERSION}-${TIMESTAMP}.tar.gz"
    log "3. Install: cd baikao-platform && ./install.sh --help"
}

# Run main function
main "$@"
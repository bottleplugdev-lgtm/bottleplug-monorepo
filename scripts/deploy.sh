#!/bin/bash

# Enhanced deployment script for BottlePlug
# This script handles both local and remote deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_DIR="/opt/bottleplug"
BACKUP_DIR="$DEPLOYMENT_DIR/backup"
LOG_DIR="$DEPLOYMENT_DIR/logs"
COMPOSE_FILE="docker-compose.prod.yml"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    log "Checking requirements..."
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "docker-compose.prod.yml not found. Are you in the right directory?"
        exit 1
    fi
    
    if [ ! -f ".env.prod" ]; then
        error ".env.prod not found. Please create it from env.prod.template"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    success "All requirements met"
}

create_backup() {
    log "Creating backup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Create timestamp
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    # Backup database if containers are running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log "Backing up database..."
        docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U bottleplug bottleplug_prod > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql" || warning "Database backup failed"
    fi
    
    # Backup environment files
    cp .env.prod "$BACKUP_DIR/env.prod.backup_$TIMESTAMP" 2>/dev/null || true
    
    # Clean old backups (keep last 7 days)
    find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "*.backup_*" -mtime +7 -delete 2>/dev/null || true
    
    success "Backup created"
}

pull_changes() {
    log "Pulling latest changes from git..."
    
    if [ -d ".git" ]; then
        git fetch origin
        git reset --hard origin/main
        success "Git changes pulled"
    else
        warning "Not a git repository, skipping git pull"
    fi
}

stop_containers() {
    log "Stopping current containers..."
    
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        docker-compose -f "$COMPOSE_FILE" down --timeout 30
        success "Containers stopped"
    else
        log "No running containers found"
    fi
}

build_and_start() {
    log "Building and starting containers..."
    
    # Build with no cache for fresh builds
    docker-compose -f "$COMPOSE_FILE" build --no-cache --parallel
    
    # Start containers
    docker-compose -f "$COMPOSE_FILE" up -d
    
    success "Containers built and started"
}

wait_for_services() {
    log "Waiting for services to be healthy..."
    
    # Wait for database
    log "Waiting for database..."
    for i in {1..30}; do
        if docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U bottleplug > /dev/null 2>&1; then
            success "Database is ready"
            break
        fi
        sleep 2
    done
    
    # Wait for backend
    log "Waiting for backend..."
    for i in {1..30}; do
        if docker-compose -f "$COMPOSE_FILE" exec -T backend curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
            success "Backend is ready"
            break
        fi
        sleep 2
    done
    
    # Additional wait for all services
    sleep 10
}

run_migrations() {
    log "Running database migrations..."
    
    docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate --noinput
    success "Migrations completed"
}

collect_static() {
    log "Collecting static files..."
    
    docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py collectstatic --noinput
    success "Static files collected"
}

cleanup() {
    log "Cleaning up old images and containers..."
    
    docker image prune -f
    docker container prune -f
    docker volume prune -f
    
    success "Cleanup completed"
}

check_deployment() {
    log "Checking deployment status..."
    
    # Check if containers are running
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        error "Some containers are not running"
        docker-compose -f "$COMPOSE_FILE" ps
        return 1
    fi
    
    # Test health endpoint
    if curl -f http://localhost/health/ > /dev/null 2>&1; then
        success "Health check passed"
    else
        warning "Health check failed - check nginx configuration"
    fi
    
    success "Deployment check completed"
}

show_status() {
    log "Deployment Summary:"
    echo ""
    echo "📊 Container Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    echo "💾 Disk Usage:"
    df -h / | tail -1
    echo ""
    echo "🧠 Memory Usage:"
    free -h
    echo ""
    echo "📝 Useful Commands:"
    echo "- View logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "- Restart services: docker-compose -f $COMPOSE_FILE restart"
    echo "- Check status: docker-compose -f $COMPOSE_FILE ps"
    echo "- Access database: docker-compose -f $COMPOSE_FILE exec db psql -U bottleplug -d bottleplug_prod"
}

# Main deployment function
deploy() {
    log "🚀 Starting BottlePlug deployment..."
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Log deployment start
    echo "$(date): Starting deployment" >> "$LOG_DIR/deployment.log"
    
    # Run deployment steps
    check_requirements
    create_backup
    pull_changes
    stop_containers
    build_and_start
    wait_for_services
    run_migrations
    collect_static
    cleanup
    check_deployment
    
    # Log successful deployment
    echo "$(date): Deployment successful" >> "$LOG_DIR/deployment.log"
    
    success "🎉 Deployment completed successfully!"
    show_status
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "backup")
        create_backup
        ;;
    "status")
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    "restart")
        docker-compose -f "$COMPOSE_FILE" restart
        ;;
    "stop")
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    "start")
        docker-compose -f "$COMPOSE_FILE" up -d
        ;;
    "help"|"-h"|"--help")
        echo "BottlePlug Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy    - Full deployment (default)"
        echo "  backup    - Create backup only"
        echo "  status    - Show container status"
        echo "  logs      - Show container logs"
        echo "  restart   - Restart all services"
        echo "  stop      - Stop all services"
        echo "  start     - Start all services"
        echo "  help      - Show this help"
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac

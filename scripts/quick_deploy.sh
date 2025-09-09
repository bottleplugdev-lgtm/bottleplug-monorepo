#!/bin/bash

# Quick deployment script for local development and testing
# This script can be used for quick deployments without full CI/CD

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"

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

# Check if we're in the right directory
check_directory() {
    if [ ! -f "docker-compose.yml" ]; then
        error "docker-compose.yml not found. Are you in the right directory?"
        exit 1
    fi
    success "Directory check passed"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker is not running. Please start Docker first."
        exit 1
    fi
    success "Docker is running"
}

# Build and start development environment
dev_deploy() {
    log "🚀 Deploying development environment..."
    
    # Stop existing containers
    docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true
    
    # Build and start
    docker-compose -f "$COMPOSE_FILE" build
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services
    log "⏳ Waiting for services to start..."
    sleep 15
    
    # Run migrations
    log "🗄️ Running migrations..."
    docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate
    
    success "🎉 Development environment deployed!"
    show_dev_info
}

# Build and start production environment
prod_deploy() {
    log "🚀 Deploying production environment..."
    
    # Check for production environment file
    if [ ! -f ".env.prod" ]; then
        error ".env.prod not found. Please create it from env.prod.template"
        exit 1
    fi
    
    # Stop existing containers
    docker-compose -f "$PROD_COMPOSE_FILE" down 2>/dev/null || true
    
    # Build and start
    docker-compose -f "$PROD_COMPOSE_FILE" build --no-cache
    docker-compose -f "$PROD_COMPOSE_FILE" up -d
    
    # Wait for services
    log "⏳ Waiting for services to start..."
    sleep 30
    
    # Run migrations
    log "🗄️ Running migrations..."
    docker-compose -f "$PROD_COMPOSE_FILE" exec -T backend python manage.py migrate
    
    # Collect static files
    log "📁 Collecting static files..."
    docker-compose -f "$PROD_COMPOSE_FILE" exec -T backend python manage.py collectstatic --noinput
    
    success "🎉 Production environment deployed!"
    show_prod_info
}

# Show development environment information
show_dev_info() {
    echo ""
    echo "📊 Development Environment:"
    echo "- Backend API: http://localhost:8000"
    echo "- E-commerce Web: http://localhost:3000"
    echo "- Admin Dashboard: http://localhost:3001"
    echo "- Database Admin: http://localhost:5050"
    echo ""
    echo "📝 Useful Commands:"
    echo "- View logs: docker-compose logs -f"
    echo "- Stop services: docker-compose down"
    echo "- Restart: docker-compose restart"
    echo "- Access backend: docker-compose exec backend bash"
    echo "- Access database: docker-compose exec db psql -U postgres -d bottleplug"
}

# Show production environment information
show_prod_info() {
    echo ""
    echo "📊 Production Environment:"
    echo "- Application: http://localhost"
    echo "- Health Check: http://localhost/health/"
    echo ""
    echo "📝 Useful Commands:"
    echo "- View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "- Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "- Restart: docker-compose -f docker-compose.prod.yml restart"
    echo "- Check status: docker-compose -f docker-compose.prod.yml ps"
}

# Clean up Docker resources
cleanup() {
    log "🧹 Cleaning up Docker resources..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    success "Cleanup completed"
}

# Show help
show_help() {
    echo "BottlePlug Quick Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  dev       - Deploy development environment (default)"
    echo "  prod      - Deploy production environment"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  logs      - Show logs"
    echo "  status    - Show container status"
    echo "  cleanup   - Clean up Docker resources"
    echo "  help      - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 dev     # Deploy development environment"
    echo "  $0 prod    # Deploy production environment"
    echo "  $0 logs    # View logs"
    echo "  $0 cleanup # Clean up Docker resources"
}

# Main function
main() {
    case "${1:-dev}" in
        "dev")
            check_directory
            check_docker
            dev_deploy
            ;;
        "prod")
            check_directory
            check_docker
            prod_deploy
            ;;
        "stop")
            log "🛑 Stopping all services..."
            docker-compose -f "$COMPOSE_FILE" down 2>/dev/null || true
            docker-compose -f "$PROD_COMPOSE_FILE" down 2>/dev/null || true
            success "All services stopped"
            ;;
        "restart")
            log "🔄 Restarting services..."
            docker-compose -f "$COMPOSE_FILE" restart 2>/dev/null || true
            docker-compose -f "$PROD_COMPOSE_FILE" restart 2>/dev/null || true
            success "Services restarted"
            ;;
        "logs")
            if [ -f "$PROD_COMPOSE_FILE" ] && docker-compose -f "$PROD_COMPOSE_FILE" ps | grep -q "Up"; then
                docker-compose -f "$PROD_COMPOSE_FILE" logs -f
            else
                docker-compose -f "$COMPOSE_FILE" logs -f
            fi
            ;;
        "status")
            echo "📊 Container Status:"
            echo ""
            echo "Development Environment:"
            docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null || echo "Not running"
            echo ""
            echo "Production Environment:"
            docker-compose -f "$PROD_COMPOSE_FILE" ps 2>/dev/null || echo "Not running"
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            error "Unknown command: $1"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

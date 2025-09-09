#!/bin/bash

# Test script for deployment pipeline
# This script validates the deployment setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Test functions
test_docker() {
    log "Testing Docker installation..."
    if command -v docker &> /dev/null; then
        if docker info > /dev/null 2>&1; then
            success "Docker is installed and running"
        else
            error "Docker is installed but not running"
            return 1
        fi
    else
        error "Docker is not installed"
        return 1
    fi
}

test_docker_compose() {
    log "Testing Docker Compose installation..."
    if command -v docker-compose &> /dev/null; then
        success "Docker Compose is installed"
    else
        error "Docker Compose is not installed"
        return 1
    fi
}

test_files() {
    log "Testing required files..."
    
    local files=(
        "docker-compose.yml"
        "docker-compose.prod.yml"
        "env.prod.template"
        "scripts/deploy.sh"
        "scripts/quick_deploy.sh"
        "scripts/setup_digital_ocean.sh"
        ".github/workflows/deploy.yml"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            success "Found $file"
        else
            error "Missing $file"
            return 1
        fi
    done
}

test_scripts() {
    log "Testing script permissions..."
    
    local scripts=(
        "scripts/deploy.sh"
        "scripts/quick_deploy.sh"
        "scripts/setup_digital_ocean.sh"
        "scripts/setup_git_deployment.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ -x "$script" ]; then
                success "$script is executable"
            else
                warning "$script is not executable, fixing..."
                chmod +x "$script"
                success "$script is now executable"
            fi
        else
            warning "$script not found"
        fi
    done
}

test_environment() {
    log "Testing environment configuration..."
    
    if [ -f ".env.prod" ]; then
        success ".env.prod exists"
        
        # Check for required variables
        local required_vars=(
            "POSTGRES_PASSWORD"
            "SECRET_KEY"
            "ALLOWED_HOSTS"
        )
        
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" .env.prod; then
                success "$var is configured"
            else
                warning "$var is not configured in .env.prod"
            fi
        done
    else
        warning ".env.prod not found - you'll need to create it from env.prod.template"
    fi
}

test_git() {
    log "Testing Git configuration..."
    
    if [ -d ".git" ]; then
        success "Git repository initialized"
        
        # Check for remote
        if git remote -v | grep -q "origin"; then
            success "Git remote 'origin' is configured"
        else
            warning "Git remote 'origin' is not configured"
        fi
        
        # Check current branch
        local current_branch=$(git branch --show-current)
        log "Current branch: $current_branch"
        
    else
        warning "Not a Git repository"
    fi
}

test_github_actions() {
    log "Testing GitHub Actions configuration..."
    
    if [ -f ".github/workflows/deploy.yml" ]; then
        success "GitHub Actions workflow file exists"
        
        # Check for required secrets (we can't validate the actual secrets)
        log "Required GitHub Secrets:"
        echo "  - HOST: Your server IP address"
        echo "  - USERNAME: SSH username (usually 'root')"
        echo "  - SSH_KEY: Your private SSH key"
        echo "  - PORT: SSH port (usually 22)"
        echo "  - SLACK_WEBHOOK: (optional) Slack webhook URL"
        
    else
        error "GitHub Actions workflow file not found"
        return 1
    fi
}

test_docker_build() {
    log "Testing Docker build capability..."
    
    # Test if we can build the backend
    if [ -f "backend/Dockerfile" ]; then
        log "Testing backend Docker build..."
        if docker build -t bottleplug-backend-test ./backend > /dev/null 2>&1; then
            success "Backend Docker build successful"
            docker rmi bottleplug-backend-test > /dev/null 2>&1 || true
        else
            warning "Backend Docker build failed"
        fi
    fi
    
    # Test if we can build the frontend
    if [ -f "web/Dockerfile" ]; then
        log "Testing frontend Docker build..."
        if docker build -t bottleplug-frontend-test ./web > /dev/null 2>&1; then
            success "Frontend Docker build successful"
            docker rmi bottleplug-frontend-test > /dev/null 2>&1 || true
        else
            warning "Frontend Docker build failed"
        fi
    fi
}

show_summary() {
    echo ""
    echo "📊 Deployment Test Summary"
    echo "=========================="
    echo ""
    echo "✅ Ready for deployment:"
    echo "  - Docker and Docker Compose installed"
    echo "  - Required files present"
    echo "  - Scripts are executable"
    echo "  - GitHub Actions configured"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Create Digital Ocean droplet"
    echo "2. Run: ./scripts/setup_digital_ocean.sh"
    echo "3. Configure .env.prod with your values"
    echo "4. Deploy: ./scripts/deploy.sh"
    echo ""
    echo "🔧 Quick Commands:"
    echo "  - Test locally: ./scripts/quick_deploy.sh dev"
    echo "  - Deploy to production: ./scripts/deploy.sh"
    echo "  - Check status: ./scripts/quick_deploy.sh status"
    echo ""
    echo "📚 Documentation:"
    echo "  - Full guide: DEPLOYMENT_GUIDE.md"
    echo "  - API docs: API_ENDPOINTS_ORGANIZATION.md"
    echo ""
}

# Main test function
main() {
    log "🧪 Testing BottlePlug deployment setup..."
    echo ""
    
    local tests_passed=0
    local tests_failed=0
    
    # Run tests
    test_docker && ((tests_passed++)) || ((tests_failed++))
    test_docker_compose && ((tests_passed++)) || ((tests_failed++))
    test_files && ((tests_passed++)) || ((tests_failed++))
    test_scripts && ((tests_passed++)) || ((tests_failed++))
    test_environment && ((tests_passed++)) || ((tests_failed++))
    test_git && ((tests_passed++)) || ((tests_failed++))
    test_github_actions && ((tests_passed++)) || ((tests_failed++))
    test_docker_build && ((tests_passed++)) || ((tests_failed++))
    
    echo ""
    echo "📊 Test Results:"
    echo "  ✅ Passed: $tests_passed"
    echo "  ❌ Failed: $tests_failed"
    echo ""
    
    if [ $tests_failed -eq 0 ]; then
        success "🎉 All tests passed! Your deployment setup is ready."
        show_summary
    else
        warning "⚠️ Some tests failed. Please review the issues above."
        echo ""
        echo "Common fixes:"
        echo "  - Install Docker: https://docs.docker.com/get-docker/"
        echo "  - Install Docker Compose: https://docs.docker.com/compose/install/"
        echo "  - Create .env.prod from env.prod.template"
        echo "  - Initialize Git repository: git init && git remote add origin <your-repo-url>"
    fi
}

# Run main function
main

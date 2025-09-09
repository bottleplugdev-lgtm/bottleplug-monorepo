#!/bin/bash

# Setup script for Git-based deployment
# This script sets up a bare git repository for automatic deployments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
GIT_REPO_DIR="/opt/bottleplug.git"
DEPLOYMENT_DIR="/opt/bottleplug"
REPO_URL="https://github.com/yourusername/bottleplug-monorepo.git"  # Update this

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Please run this script as root"
        exit 1
    fi
}

# Create bare git repository
setup_bare_repo() {
    log "Setting up bare git repository..."
    
    # Create bare repository
    mkdir -p "$GIT_REPO_DIR"
    cd "$GIT_REPO_DIR"
    git init --bare
    
    # Set up post-receive hook
    cat > hooks/post-receive << 'EOF'
#!/bin/bash

# Git post-receive hook for automatic deployment
set -e

DEPLOYMENT_DIR="/opt/bottleplug"
LOG_FILE="$DEPLOYMENT_DIR/logs/git_deploy.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Read the ref that was pushed
while read oldrev newrev refname; do
    # Only deploy if pushing to main/master branch
    if [[ $refname == "refs/heads/main" ]] || [[ $refname == "refs/heads/master" ]]; then
        log "Git push detected on $refname, starting deployment..."
        
        # Change to deployment directory
        cd "$DEPLOYMENT_DIR"
        
        # Pull latest changes
        log "Pulling latest changes..."
        git fetch origin
        git reset --hard origin/main
        
        # Run deployment script
        log "Running deployment..."
        if [ -f "./scripts/deploy.sh" ]; then
            ./scripts/deploy.sh deploy
            log "Deployment completed successfully!"
        else
            log "ERROR: Deployment script not found!"
            exit 1
        fi
    else
        log "Push to $refname ignored (not main/master branch)"
    fi
done
EOF
    
    # Make hook executable
    chmod +x hooks/post-receive
    
    # Set ownership
    chown -R bottleplug:bottleplug "$GIT_REPO_DIR"
    
    success "Bare git repository created"
}

# Clone repository for deployment
clone_repo() {
    log "Cloning repository for deployment..."
    
    # Remove existing directory if it exists
    if [ -d "$DEPLOYMENT_DIR" ]; then
        rm -rf "$DEPLOYMENT_DIR"
    fi
    
    # Clone repository
    git clone "$REPO_URL" "$DEPLOYMENT_DIR"
    
    # Set ownership
    chown -R bottleplug:bottleplug "$DEPLOYMENT_DIR"
    
    success "Repository cloned for deployment"
}

# Set up SSH key for git operations
setup_ssh_key() {
    log "Setting up SSH key for git operations..."
    
    # Create .ssh directory for bottleplug user
    sudo -u bottleplug mkdir -p /home/bottleplug/.ssh
    sudo -u bottleplug chmod 700 /home/bottleplug/.ssh
    
    # Generate SSH key if it doesn't exist
    if [ ! -f "/home/bottleplug/.ssh/id_rsa" ]; then
        sudo -u bottleplug ssh-keygen -t rsa -b 4096 -f /home/bottleplug/.ssh/id_rsa -N ""
    fi
    
    # Set proper permissions
    sudo -u bottleplug chmod 600 /home/bottleplug/.ssh/id_rsa
    sudo -u bottleplug chmod 644 /home/bottleplug/.ssh/id_rsa.pub
    
    success "SSH key set up"
    echo ""
    echo "📋 Add this public key to your GitHub repository:"
    echo "   - Go to GitHub → Settings → Deploy keys"
    echo "   - Add the following public key:"
    echo ""
    cat /home/bottleplug/.ssh/id_rsa.pub
    echo ""
}

# Configure git user
configure_git() {
    log "Configuring git user..."
    
    # Set git user for bottleplug
    sudo -u bottleplug git config --global user.name "BottlePlug Deploy"
    sudo -u bottleplug git config --global user.email "deploy@bottleplug.com"
    
    # Set up SSH for GitHub
    sudo -u bottleplug ssh-keyscan github.com >> /home/bottleplug/.ssh/known_hosts
    
    success "Git configured"
}

# Create deployment instructions
create_instructions() {
    log "Creating deployment instructions..."
    
    cat > "$DEPLOYMENT_DIR/DEPLOYMENT_INSTRUCTIONS.md" << EOF
# BottlePlug Git Deployment Instructions

## Setup Complete! 🎉

Your server is now configured for automatic git-based deployments.

## How to Deploy

### Method 1: GitHub Actions (Recommended)
1. Push your code to the main branch
2. GitHub Actions will automatically deploy to your server

### Method 2: Direct Git Push
1. Add this server as a remote:
   \`\`\`bash
   git remote add production bottleplug@$(curl -s ifconfig.me):/opt/bottleplug.git
   \`\`\`

2. Push to deploy:
   \`\`\`bash
   git push production main
   \`\`\`

### Method 3: Manual Deployment
1. SSH into your server
2. Run: \`cd /opt/bottleplug && ./scripts/deploy.sh\`

## Server Information
- **Git Repository**: $GIT_REPO_DIR
- **Deployment Directory**: $DEPLOYMENT_DIR
- **SSH User**: bottleplug
- **Server IP**: $(curl -s ifconfig.me)

## Next Steps
1. Add your GitHub public key to the repository
2. Configure your environment variables in \`.env.prod\`
3. Copy your Firebase credentials
4. Run your first deployment

## Useful Commands
- View deployment logs: \`tail -f $DEPLOYMENT_DIR/logs/git_deploy.log\`
- Check container status: \`docker-compose -f $DEPLOYMENT_DIR/docker-compose.prod.yml ps\`
- View application logs: \`docker-compose -f $DEPLOYMENT_DIR/docker-compose.prod.yml logs -f\`
- Manual backup: \`$DEPLOYMENT_DIR/backup.sh\`

## Troubleshooting
- If deployment fails, check the logs in \`$DEPLOYMENT_DIR/logs/\`
- Ensure all environment variables are set in \`.env.prod\`
- Verify Firebase credentials are in place
- Check Docker containers are running: \`docker ps\`
EOF
    
    success "Deployment instructions created"
}

# Main setup function
main() {
    log "🚀 Setting up Git-based deployment..."
    
    check_root
    setup_bare_repo
    clone_repo
    setup_ssh_key
    configure_git
    create_instructions
    
    success "🎉 Git deployment setup completed!"
    
    echo ""
    echo "📋 Next Steps:"
    echo "1. Add the SSH public key to your GitHub repository"
    echo "2. Configure environment variables in $DEPLOYMENT_DIR/.env.prod"
    echo "3. Copy Firebase credentials to $DEPLOYMENT_DIR/"
    echo "4. Test deployment by pushing to main branch"
    echo ""
    echo "📚 Documentation created at: $DEPLOYMENT_DIR/DEPLOYMENT_INSTRUCTIONS.md"
}

# Run main function
main

#!/bin/bash

# Digital Ocean Server Setup Script for BottlePlug
# This script sets up a fresh Digital Ocean droplet for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/bottleplug"
REPO_URL="https://github.com/bottleplugdev-lgtm/bottleplug-monorepo.git"

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

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Please run this script as root"
        exit 1
    fi
}

# Update system packages
update_system() {
    log "Updating system packages..."
    apt update && apt upgrade -y
    success "System updated"
}

# Install essential packages
install_packages() {
    log "Installing essential packages..."
    apt install -y \
        curl \
        wget \
        git \
        nginx \
        certbot \
        python3-certbot-nginx \
        ufw \
        fail2ban \
        htop \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    success "Essential packages installed"
}

# Install Docker
install_docker() {
    log "Installing Docker..."
    
    # Remove old Docker installations
    apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up the stable repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index
    apt update
    
    # Install Docker Engine
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    success "Docker installed and started"
}

# Install Docker Compose
install_docker_compose() {
    log "Installing Docker Compose..."
    
    # Download latest version
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Create symlink for docker-compose command
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    success "Docker Compose installed"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    # Reset UFW
    ufw --force reset
    
    # Set default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow essential services
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Enable firewall
    ufw --force enable
    
    success "Firewall configured"
}

# Configure fail2ban
configure_fail2ban() {
    log "Configuring fail2ban..."
    
    # Create jail.local configuration
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF
    
    # Start and enable fail2ban
    systemctl enable fail2ban
    systemctl start fail2ban
    
    success "Fail2ban configured"
}

# Create application directory and user
setup_application() {
    log "Setting up application directory..."
    
    # Create application directory
    mkdir -p "$APP_DIR"
    cd "$APP_DIR"
    
    # Create application user
    if ! id "bottleplug" &>/dev/null; then
        useradd -r -s /bin/bash -d "$APP_DIR" bottleplug
        usermod -aG docker bottleplug
    fi
    
    # Set ownership
    chown -R bottleplug:bottleplug "$APP_DIR"
    
    # Create necessary directories
    mkdir -p "$APP_DIR/backup" "$APP_DIR/logs" "$APP_DIR/ssl"
    
    success "Application directory set up"
}

# Configure log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    cat > /etc/logrotate.d/bottleplug << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 bottleplug bottleplug
    postrotate
        docker-compose -f $APP_DIR/docker-compose.prod.yml restart nginx > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
EOF
    
    success "Log rotation configured"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > /etc/systemd/system/bottleplug.service << EOF
[Unit]
Description=BottlePlug Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
ExecReload=/usr/local/bin/docker-compose -f docker-compose.prod.yml restart
TimeoutStartSec=0
User=bottleplug
Group=bottleplug

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable bottleplug.service
    
    success "Systemd service created"
}

# Create backup script
create_backup_script() {
    log "Creating backup script..."
    
    cat > "$APP_DIR/backup.sh" << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/bottleplug/backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_$DATE.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
echo "Creating database backup..."
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U bottleplug bottleplug_prod > $BACKUP_DIR/db_backup_$DATE.sql

# Create media backup
echo "Creating media backup..."
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz media/ 2>/dev/null || true

# Create full backup
echo "Creating full backup..."
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='backup' \
    --exclude='logs' \
    .

# Remove old backups (keep last 30 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
EOF
    
    chmod +x "$APP_DIR/backup.sh"
    chown bottleplug:bottleplug "$APP_DIR/backup.sh"
    
    success "Backup script created"
}

# Create monitoring script
create_monitoring_script() {
    log "Creating monitoring script..."
    
    cat > "$APP_DIR/monitor.sh" << 'EOF'
#!/bin/bash

LOG_FILE="/opt/bottleplug/logs/monitor.log"
ALERT_EMAIL="admin@yourdomain.com"  # Update this

# Function to log with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Check if containers are running
check_containers() {
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log_message "ALERT: Some containers are not running!"
        # You can add notification logic here (email, Slack, etc.)
        return 1
    fi
    return 0
}

# Check disk space
check_disk_space() {
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 80 ]; then
        log_message "ALERT: Disk usage is above 80% ($DISK_USAGE%)"
        return 1
    fi
    return 0
}

# Check memory usage
check_memory() {
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ $MEMORY_USAGE -gt 80 ]; then
        log_message "ALERT: Memory usage is above 80% ($MEMORY_USAGE%)"
        return 1
    fi
    return 0
}

# Check application health
check_health() {
    if ! curl -f http://localhost/health/ > /dev/null 2>&1; then
        log_message "ALERT: Application health check failed"
        return 1
    fi
    return 0
}

# Run all checks
main() {
    log_message "Starting health checks..."
    
    check_containers
    check_disk_space
    check_memory
    check_health
    
    log_message "Health checks completed"
}

main
EOF
    
    chmod +x "$APP_DIR/monitor.sh"
    chown bottleplug:bottleplug "$APP_DIR/monitor.sh"
    
    success "Monitoring script created"
}

# Set up cron jobs
setup_cron_jobs() {
    log "Setting up cron jobs..."
    
    # Create cron jobs for bottleplug user
    cat > /tmp/bottleplug_cron << EOF
# Daily backup at 2 AM
0 2 * * * /opt/bottleplug/backup.sh >> /opt/bottleplug/logs/backup.log 2>&1

# Health monitoring every 5 minutes
*/5 * * * * /opt/bottleplug/monitor.sh

# Weekly system update
0 3 * * 0 apt update && apt upgrade -y >> /opt/bottleplug/logs/system_update.log 2>&1

# Monthly log cleanup
0 4 1 * * find /opt/bottleplug/logs -name "*.log" -mtime +30 -delete
EOF
    
    # Install cron jobs for bottleplug user
    crontab -u bottleplug /tmp/bottleplug_cron
    rm /tmp/bottleplug_cron
    
    success "Cron jobs set up"
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Create basic configuration (will be updated when app is deployed)
    cat > /etc/nginx/sites-available/bottleplug << EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    location / {
        return 200 'BottlePlug server is ready for deployment';
        add_header Content-Type text/plain;
    }
}
EOF
    
    # Enable the site
    ln -sf /etc/nginx/sites-available/bottleplug /etc/nginx/sites-enabled/
    
    # Test and reload nginx
    nginx -t
    systemctl reload nginx
    
    success "Nginx configured"
}

# Main setup function
main() {
    log "🚀 Setting up BottlePlug production server..."
    
    check_root
    update_system
    install_packages
    install_docker
    install_docker_compose
    configure_firewall
    configure_fail2ban
    setup_application
    setup_log_rotation
    create_systemd_service
    create_backup_script
    create_monitoring_script
    setup_cron_jobs
    configure_nginx
    
    success "🎉 Server setup completed successfully!"
    
    echo ""
    echo "📋 Next Steps:"
    echo "1. Clone your repository:"
    echo "   cd $APP_DIR"
    echo "   git clone $REPO_URL ."
    echo ""
    echo "2. Set up environment variables:"
    echo "   cp env.prod.template .env.prod"
    echo "   nano .env.prod"
    echo ""
    echo "3. Copy your Firebase credentials:"
    echo "   scp firebase-credentials.json root@$(curl -s ifconfig.me):$APP_DIR/"
    echo ""
    echo "4. Deploy your application:"
    echo "   ./scripts/deploy.sh"
    echo ""
    echo "5. Set up SSL certificate:"
    echo "   certbot --nginx -d yourdomain.com -d www.yourdomain.com"
    echo ""
    echo "🔐 Security Checklist:"
    echo "- [ ] Update SSH keys"
    echo "- [ ] Configure domain DNS"
    echo "- [ ] Set up environment variables"
    echo "- [ ] Test SSL certificate"
    echo "- [ ] Verify firewall rules"
    echo ""
    echo "📚 Useful Commands:"
    echo "- View logs: docker-compose -f $APP_DIR/docker-compose.prod.yml logs -f"
    echo "- Restart services: systemctl restart bottleplug"
    echo "- Check status: docker-compose -f $APP_DIR/docker-compose.prod.yml ps"
    echo "- Manual backup: $APP_DIR/backup.sh"
    echo "- Monitor health: $APP_DIR/monitor.sh"
}

# Run main function
main

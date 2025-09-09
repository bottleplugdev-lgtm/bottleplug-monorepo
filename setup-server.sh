#!/bin/bash

# Digital Ocean Server Setup Script for BottlePlug
# Run this script on your fresh Digital Ocean droplet

set -e

echo "🚀 Setting up BottlePlug production server..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
echo "🔧 Installing essential packages..."
apt install -y curl wget git nginx certbot python3-certbot-nginx ufw fail2ban

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
echo "🐙 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Add user to docker group
usermod -aG docker $USER

# Configure firewall
echo "🔥 Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Configure fail2ban
echo "🛡️ Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/bottleplug
cd /opt/bottleplug

# Clone repository (you'll need to update this with your actual repo)
echo "📥 Cloning repository..."
# git clone https://github.com/yourusername/your-repo.git .

# Create necessary directories
mkdir -p ssl backup logs

# Set up log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/bottleplug << EOF
/opt/bottleplug/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

# Create systemd service for auto-start
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/bottleplug.service << EOF
[Unit]
Description=BottlePlug Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/bottleplug
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
systemctl enable bottleplug.service

# Create backup script
echo "💾 Creating backup script..."
cat > /opt/bottleplug/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/bottleplug/backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_$DATE.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U bottleplug bottleplug_prod > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
tar -czf $BACKUP_DIR/$BACKUP_FILE $BACKUP_DIR/db_backup_$DATE.sql

# Remove old backups (keep last 30 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +1 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x /opt/bottleplug/backup.sh

# Set up cron job for daily backups
echo "⏰ Setting up daily backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/bottleplug/backup.sh") | crontab -

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > /opt/bottleplug/monitor.sh << 'EOF'
#!/bin/bash

# Check if containers are running
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "ALERT: Some containers are not running!"
    # You can add notification logic here (email, Slack, etc.)
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERT: Disk usage is above 80%!"
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "ALERT: Memory usage is above 80%!"
fi
EOF

chmod +x /opt/bottleplug/monitor.sh

# Set up monitoring cron job
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/bottleplug/monitor.sh") | crontab -

echo "✅ Server setup completed!"
echo ""
echo "Next steps:"
echo "1. Copy your application files to /opt/bottleplug"
echo "2. Copy env.prod.template to .env.prod and configure it"
echo "3. Copy your firebase-credentials.json to /opt/bottleplug"
echo "4. Run: docker-compose -f docker-compose.prod.yml up -d"
echo "5. Set up SSL certificate with: certbot --nginx -d yourdomain.com"
echo ""
echo "🔐 Don't forget to:"
echo "- Configure your domain DNS to point to this server"
echo "- Set up your environment variables in .env.prod"
echo "- Test your application thoroughly"
echo ""
echo "📚 Useful commands:"
echo "- View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "- Restart services: systemctl restart bottleplug"
echo "- Check status: docker-compose -f docker-compose.prod.yml ps"

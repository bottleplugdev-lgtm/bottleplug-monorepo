# BottlePlug Deployment Guide 🚀

This comprehensive guide will help you deploy your BottlePlug monorepo to Digital Ocean with automatic git updates.

## 📋 Prerequisites

- Digital Ocean account
- Domain name (optional but recommended)
- GitHub repository
- Flutterwave account for payments
- Firebase project for authentication

## 🏗️ Architecture Overview

Your BottlePlug application consists of:
- **Backend**: Django REST API with PostgreSQL
- **Frontend**: Vue.js e-commerce web application
- **Dashboard**: Vue.js admin dashboard
- **Infrastructure**: Docker containers with Nginx reverse proxy

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

1. **Create a Digital Ocean Droplet:**
   - Ubuntu 22.04 LTS
   - At least 2GB RAM, 1 CPU (recommended: 4GB RAM, 2 CPU)
   - Add your SSH key

2. **Run the setup script:**
   ```bash
   ssh root@YOUR_SERVER_IP
   curl -fsSL https://raw.githubusercontent.com/bottleplugdev-lgtm/bottleplug-monorepo/main/scripts/setup_digital_ocean.sh | bash
   ```

3. **Clone your repository:**
   ```bash
   cd /opt/bottleplug
   git clone https://github.com/bottleplugdev-lgtm/bottleplug-monorepo.git .
   ```

4. **Configure environment:**
   ```bash
   cp env.prod.template .env.prod
   nano .env.prod
   ```

5. **Deploy:**
   ```bash
   ./scripts/deploy.sh
   ```

### Option 2: Manual Setup

Follow the detailed steps in the sections below.

## 🔧 Server Setup

### 1. Create Digital Ocean Droplet

1. **Choose specifications:**
   - **OS**: Ubuntu 22.04 LTS
   - **Size**: 2GB RAM, 1 CPU (minimum) or 4GB RAM, 2 CPU (recommended)
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH key (recommended)

2. **Note your droplet's IP address**

### 2. Initial Server Configuration

```bash
# Connect to your server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y curl wget git nginx certbot python3-certbot-nginx ufw fail2ban

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Add user to docker group
usermod -aG docker $USER
```

### 3. Security Configuration

```bash
# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Configure fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

## 📁 Application Setup

### 1. Create Application Directory

```bash
# Create directory
mkdir -p /opt/bottleplug
cd /opt/bottleplug

# Clone repository
git clone https://github.com/YOUR_USERNAME/bottleplug-monorepo.git .

# Create necessary directories
mkdir -p backup logs ssl
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.prod.template .env.prod

# Edit environment variables
nano .env.prod
```

**Required Environment Variables:**

```bash
# Database Configuration
POSTGRES_DB=bottleplug_prod
POSTGRES_USER=bottleplug
POSTGRES_PASSWORD=your_secure_database_password_here

# Django Configuration
SECRET_KEY=your_very_long_and_secure_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your_server_ip
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Flutterwave Payment Configuration
FLUTTERWAVE_PUBLIC_KEY=your_flutterwave_public_key
FLUTTERWAVE_SECRET_KEY=your_flutterwave_secret_key
FLUTTERWAVE_ENCRYPTION_KEY=your_flutterwave_encryption_key

# Frontend Configuration
VITE_API_BASE_URL=https://yourdomain.com/api/v1
REACT_APP_API_BASE_URL=https://yourdomain.com/api/v1

# PgAdmin Configuration (Optional)
PGADMIN_EMAIL=admin@yourdomain.com
PGADMIN_PASSWORD=your_pgadmin_password
```

### 3. Firebase Configuration

```bash
# Copy Firebase credentials
scp firebase-credentials.json root@YOUR_SERVER_IP:/opt/bottleplug/
```

## 🐳 Docker Deployment

### 1. Build and Start Containers

```bash
# Build containers
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 2. Run Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Create superuser (optional)
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## 🌐 Domain and SSL Setup

### 1. Configure Domain DNS

- Add A record: `yourdomain.com` → `YOUR_SERVER_IP`
- Add CNAME record: `www.yourdomain.com` → `yourdomain.com`

### 2. Install SSL Certificate

```bash
# Install SSL certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test SSL renewal
certbot renew --dry-run
```

## 🔄 Automatic Deployment Setup

### Option 1: GitHub Actions (Recommended)

1. **Add secrets to your GitHub repository:**
   - Go to Settings → Secrets and variables → Actions
   - Add these secrets:
     - `HOST`: Your server IP address
     - `USERNAME`: root (or your SSH user)
     - `SSH_KEY`: Your private SSH key
     - `PORT`: 22 (or your SSH port)
     - `SLACK_WEBHOOK`: (optional) Slack webhook for notifications

2. **Push to main branch to trigger deployment:**
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

### Option 2: Git Hooks

```bash
# Set up git-based deployment
./scripts/setup_git_deployment.sh

# Add server as remote
git remote add production bottleplug@YOUR_SERVER_IP:/opt/bottleplug.git

# Deploy by pushing
git push production main
```

## 📊 Monitoring and Maintenance

### 1. Health Checks

```bash
# Check application health
curl -I https://yourdomain.com/health/

# Check container status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 2. Backup Strategy

```bash
# Manual backup
./backup.sh

# Automated daily backups (already configured)
# Runs daily at 2 AM via cron
```

### 3. System Monitoring

```bash
# Check system resources
htop
df -h
free -h

# Monitor application
./monitor.sh
```

## 🛠️ Useful Commands

### Application Management

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop services
docker-compose -f docker-compose.prod.yml down

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Database Management

```bash
# Access database
docker-compose -f docker-compose.prod.yml exec db psql -U bottleplug -d bottleplug_prod

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Database backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U bottleplug bottleplug_prod > backup.sql
```

### Deployment Scripts

```bash
# Full deployment
./scripts/deploy.sh

# Quick development deployment
./scripts/quick_deploy.sh dev

# Production deployment
./scripts/quick_deploy.sh prod

# Check status
./scripts/quick_deploy.sh status

# View logs
./scripts/quick_deploy.sh logs

# Cleanup Docker resources
./scripts/quick_deploy.sh cleanup
```

## 🔧 Troubleshooting

### Common Issues

1. **Containers won't start:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs
   ```

2. **Database connection issues:**
   - Check if database container is running
   - Verify environment variables
   - Check database logs

3. **SSL certificate issues:**
   ```bash
   certbot renew --dry-run
   ```

4. **Memory issues:**
   - Increase droplet size
   - Optimize Docker containers
   - Check for memory leaks

### Performance Optimization

1. **Enable Redis caching**
2. **Optimize database queries**
3. **Use CDN for static files**
4. **Enable gzip compression**
5. **Set up monitoring alerts**

## 🔐 Security Checklist

- [ ] Firewall configured (UFW)
- [ ] Fail2ban enabled
- [ ] SSH key authentication only
- [ ] SSL certificate installed
- [ ] Environment variables secured
- [ ] Database passwords strong
- [ ] Regular backups scheduled
- [ ] Monitoring alerts set up

## 📈 Scaling Considerations

### Horizontal Scaling

- Use Digital Ocean Load Balancer
- Deploy multiple application instances
- Use managed PostgreSQL database
- Implement Redis clustering

### Vertical Scaling

- Increase droplet size
- Optimize application code
- Use CDN for static assets
- Implement caching strategies

## 🆘 Support

If you encounter issues:

1. Check the logs first
2. Review this documentation
3. Check GitHub Issues
4. Contact support

---

**Happy Deploying! 🚀**

For more information, visit the [BottlePlug Documentation](https://github.com/bottleplugdev-lgtm/bottleplug-monorepo/wiki).

# BottlePlug Production Deployment Guide

This guide will help you deploy your BottlePlug application to Digital Ocean with automatic GitHub updates.

## Prerequisites

- Digital Ocean account
- Domain name (optional but recommended)
- GitHub repository
- Flutterwave account for payments
- Firebase project for authentication

## Step 1: Create Digital Ocean Droplet

1. **Create a new droplet:**
   - Choose Ubuntu 22.04 LTS
   - Select at least 2GB RAM, 1 CPU (recommended: 4GB RAM, 2 CPU)
   - Choose a datacenter close to your users
   - Add your SSH key
   - Enable monitoring

2. **Note your droplet's IP address** - you'll need this later

## Step 2: Initial Server Setup

1. **Connect to your server:**
   ```bash
   ssh root@YOUR_SERVER_IP
   ```

2. **Run the setup script:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/setup-server.sh | bash
   ```

3. **Logout and login again** to apply Docker group changes:
   ```bash
   exit
   ssh root@YOUR_SERVER_IP
   ```

## Step 3: Deploy Your Application

1. **Navigate to the application directory:**
   ```bash
   cd /opt/bottleplug
   ```

2. **Clone your repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .
   ```

3. **Set up environment variables:**
   ```bash
   cp env.prod.template .env.prod
   nano .env.prod
   ```

4. **Configure your environment variables:**
   ```bash
   # Database
   POSTGRES_PASSWORD=your_secure_password_here
   
   # Django
   SECRET_KEY=your_very_long_secret_key_here
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_SERVER_IP
   CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   
   # Flutterwave
   FLUTTERWAVE_PUBLIC_KEY=your_public_key
   FLUTTERWAVE_SECRET_KEY=your_secret_key
   FLUTTERWAVE_ENCRYPTION_KEY=your_encryption_key
   
   # Frontend
   VITE_API_BASE_URL=https://yourdomain.com/api/v1
   ```

5. **Add your Firebase credentials:**
   ```bash
   # Copy your firebase-credentials.json to the server
   scp firebase-credentials.json root@YOUR_SERVER_IP:/opt/bottleplug/
   ```

6. **Start the application:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

7. **Check if everything is running:**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

## Step 4: Set Up Domain and SSL

1. **Point your domain to your server:**
   - Add an A record: `yourdomain.com` → `YOUR_SERVER_IP`
   - Add a CNAME record: `www.yourdomain.com` → `yourdomain.com`

2. **Install SSL certificate:**
   ```bash
   certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

3. **Test SSL:**
   ```bash
   curl -I https://yourdomain.com
   ```

## Step 5: Configure GitHub Actions

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
   git commit -m "Initial production deployment"
   git push origin main
   ```

## Step 6: Verify Deployment

1. **Check application status:**
   ```bash
   curl -I https://yourdomain.com
   ```

2. **Test API endpoints:**
   ```bash
   curl https://yourdomain.com/api/v1/health/
   ```

3. **Check logs:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

## Useful Commands

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
```

### Backup and Restore
```bash
# Manual backup
/opt/bottleplug/backup.sh

# Restore from backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U bottleplug -d bottleplug_prod < backup/db_backup_YYYYMMDD_HHMMSS.sql
```

### Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check container status
docker-compose -f docker-compose.prod.yml ps
docker stats

# View application logs
tail -f /opt/bottleplug/logs/*.log
```

## Troubleshooting

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

## Security Checklist

- [ ] Firewall configured (UFW)
- [ ] Fail2ban enabled
- [ ] SSH key authentication only
- [ ] SSL certificate installed
- [ ] Environment variables secured
- [ ] Database passwords strong
- [ ] Regular backups scheduled
- [ ] Monitoring alerts set up

## Maintenance

### Daily
- Check application logs
- Monitor system resources
- Verify backups

### Weekly
- Update system packages
- Review security logs
- Test backup restoration

### Monthly
- Update dependencies
- Review and rotate secrets
- Performance analysis

## Support

If you encounter issues:
1. Check the logs first
2. Review this documentation
3. Check GitHub Issues
4. Contact support

---

**Happy Deploying! 🚀**

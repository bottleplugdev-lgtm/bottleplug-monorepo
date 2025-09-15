#!/bin/bash

# SSL Certificate Setup Script for BottlePlug Domains
# This script sets up SSL certificates using Let's Encrypt for all domains

set -e

echo "🔐 Setting up SSL certificates for BottlePlug domains..."

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# Create SSL directory
mkdir -p /opt/bottleplug/ssl

# Generate self-signed certificates for initial setup
echo "🔧 Generating self-signed certificates for initial setup..."

# Create self-signed certificate for bottleplug.com
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /opt/bottleplug/ssl/key.pem \
    -out /opt/bottleplug/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=bottleplug.com"

echo "✅ Self-signed certificates generated successfully!"

# Function to setup Let's Encrypt certificate
setup_letsencrypt() {
    echo "🌐 Setting up Let's Encrypt certificates..."
    
    # Stop nginx temporarily
    docker-compose -f docker-compose.prod.yml --env-file .env.prod stop nginx
    
    # Get certificates for all domains
    certbot certonly --standalone \
        --email admin@bottleplug.com \
        --agree-tos \
        --no-eff-email \
        -d bottleplug.com \
        -d www.bottleplug.com \
        -d admin.bottleplug.com \
        -d api.bottleplug.com \
        -d docs.bottleplug.com \
        -d db.bottleplug.com
    
    # Copy certificates to our SSL directory
    cp /etc/letsencrypt/live/bottleplug.com/fullchain.pem /opt/bottleplug/ssl/cert.pem
    cp /etc/letsencrypt/live/bottleplug.com/privkey.pem /opt/bottleplug/ssl/key.pem
    
    # Set proper permissions
    chmod 600 /opt/bottleplug/ssl/key.pem
    chmod 644 /opt/bottleplug/ssl/cert.pem
    
    echo "✅ Let's Encrypt certificates installed successfully!"
    
    # Restart nginx
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d nginx
}

# Function to setup auto-renewal
setup_auto_renewal() {
    echo "🔄 Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > /opt/bottleplug/ssl/renew.sh << 'EOF'
#!/bin/bash
cd /opt/bottleplug
certbot renew --quiet
if [ $? -eq 0 ]; then
    cp /etc/letsencrypt/live/bottleplug.com/fullchain.pem /opt/bottleplug/ssl/cert.pem
    cp /etc/letsencrypt/live/bottleplug.com/privkey.pem /opt/bottleplug/ssl/key.pem
    docker-compose -f docker-compose.prod.yml --env-file .env.prod restart nginx
    echo "$(date): Certificates renewed successfully" >> /opt/bottleplug/ssl/renewal.log
fi
EOF
    
    chmod +x /opt/bottleplug/ssl/renew.sh
    
    # Add to crontab for automatic renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /opt/bottleplug/ssl/renew.sh") | crontab -
    
    echo "✅ Auto-renewal setup complete!"
}

# Main execution
echo "🚀 Starting SSL certificate setup..."

# For now, use self-signed certificates
echo "📝 Using self-signed certificates for initial setup"
echo "🔗 You can later run: ./scripts/setup_ssl_certificates.sh --letsencrypt"
echo "   to switch to Let's Encrypt certificates"

# Check if --letsencrypt flag is passed
if [[ "$1" == "--letsencrypt" ]]; then
    setup_letsencrypt
    setup_auto_renewal
fi

echo "🎉 SSL certificate setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure DNS records in your domain registrar"
echo "2. Test the domains once DNS propagates"
echo "3. Run './scripts/setup_ssl_certificates.sh --letsencrypt' for production certificates"
echo ""
echo "🌐 Your domains will be available at:"
echo "   - https://bottleplug.com (Main Website)"
echo "   - https://admin.bottleplug.com (Admin Dashboard)"
echo "   - https://api.bottleplug.com (Backend API)"
echo "   - https://docs.bottleplug.com (API Documentation)"
echo "   - https://db.bottleplug.com (Database Admin)"

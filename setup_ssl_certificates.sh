#!/bin/bash

# Setup SSL certificates for all domains
echo "Setting up SSL certificates for all domains..."

# Create SSL directory if it doesn't exist
mkdir -p /opt/bottleplug/ssl

# Copy main domain certificate
echo "Setting up certificate for bottleplugug.com..."
cp /etc/letsencrypt/live/bottleplugug.com/fullchain.pem /opt/bottleplug/ssl/bottleplugug.com.crt
cp /etc/letsencrypt/live/bottleplugug.com/privkey.pem /opt/bottleplug/ssl/bottleplugug.com.key

# Copy subdomain certificates
echo "Setting up certificate for docs.bottleplugug.com and api.bottleplugug.com..."
cp /etc/letsencrypt/live/docs.bottleplugug.com/fullchain.pem /opt/bottleplug/ssl/docs.bottleplugug.com.crt
cp /etc/letsencrypt/live/docs.bottleplugug.com/privkey.pem /opt/bottleplug/ssl/docs.bottleplugug.com.key

# For domains without specific certificates, use the main domain certificate
echo "Setting up fallback certificates..."
cp /opt/bottleplug/ssl/bottleplugug.com.crt /opt/bottleplug/ssl/cert.pem
cp /opt/bottleplug/ssl/bottleplugug.com.key /opt/bottleplug/ssl/key.pem

echo "SSL certificates setup complete!"
echo "Certificate files created:"
ls -la /opt/bottleplug/ssl/

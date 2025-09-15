# 🌐 Domain Setup Guide for BottlePlug

## 📋 Overview
This guide will help you set up your domains and get your BottlePlug application running with custom domains instead of IP addresses.

## 🎯 Your Domains
- **Main Website**: `bottleplugug.com`
- **Admin Dashboard**: `admin.bottleplugug.com`
- **Backend API**: `api.bottleplugug.com`
- **API Documentation**: `docs.bottleplugug.com`
- **Database Admin**: `db.bottleplugug.com`

## 🔧 Step 1: Configure DNS Records

### In Your Domain Registrar:
Add these DNS records (A records) pointing to your Digital Ocean IP:

```
Type: A Record
Name: @ (or bottleplugug.com)
Value: 146.190.126.50
TTL: 300 (5 minutes)

Type: A Record
Name: www
Value: 146.190.126.50
TTL: 300

Type: A Record
Name: admin
Value: 146.190.126.50
TTL: 300

Type: A Record
Name: api
Value: 146.190.126.50
TTL: 300

Type: A Record
Name: docs
Value: 146.190.126.50
TTL: 300

Type: A Record
Name: db
Value: 146.190.126.50
TTL: 300
```

## 🚀 Step 2: Deploy Updated Configuration

### Push the updated Nginx configuration:
```bash
git add .
git commit -m "Add domain-specific Nginx configuration"
git push origin main
```

### On your server, pull the updates:
```bash
cd /opt/bottleplug
git pull origin main
```

## 🔐 Step 3: Set Up SSL Certificates

### Initial Setup (Self-signed certificates):
```bash
cd /opt/bottleplug
./scripts/setup_ssl_certificates.sh
```

### Production Setup (Let's Encrypt certificates):
```bash
cd /opt/bottleplug
./scripts/setup_ssl_certificates.sh --letsencrypt
```

## 🔄 Step 4: Restart Services

```bash
cd /opt/bottleplug
docker-compose -f docker-compose.prod.yml --env-file .env.prod down
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## ⏱️ Step 5: Wait for DNS Propagation

- **DNS propagation** typically takes 5-30 minutes
- **Can take up to 24 hours** in some cases
- **Test with**: `nslookup bottleplug.com`

## 🧪 Step 6: Test Your Domains

### Test DNS Resolution:
```bash
nslookup bottleplugug.com
nslookup admin.bottleplugug.com
nslookup api.bottleplugug.com
```

### Test Website Access:
- **Main Website**: https://bottleplugug.com
- **Admin Dashboard**: https://admin.bottleplugug.com
- **Backend API**: https://api.bottleplugug.com
- **API Documentation**: https://docs.bottleplugug.com
- **Database Admin**: https://db.bottleplugug.com

## 🔍 Troubleshooting

### If domains don't work:

1. **Check DNS propagation**:
   ```bash
   nslookup bottleplugug.com
   ```

2. **Check if containers are running**:
   ```bash
   docker ps
   ```

3. **Check Nginx logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod logs nginx
   ```

4. **Check SSL certificates**:
   ```bash
   ls -la /opt/bottleplug/ssl/
   ```

5. **Test with curl**:
   ```bash
   curl -I https://bottleplugug.com
   ```

### Common Issues:

- **DNS not propagated**: Wait longer or check DNS settings
- **SSL certificate errors**: Run the SSL setup script again
- **Connection refused**: Check if containers are running
- **502 Bad Gateway**: Check backend container logs

## 📱 Mobile App Configuration

Update your mobile app to use the new API domain:
```javascript
// Change from:
const API_BASE_URL = 'http://146.190.126.50:8000';

// To:
const API_BASE_URL = 'https://api.bottleplug.com';
```

## 🔒 Security Notes

- **HTTPS is enforced** for all domains
- **HTTP redirects to HTTPS** automatically
- **Security headers** are configured
- **Rate limiting** is enabled for API endpoints

## 📊 Monitoring

### Health Check Endpoints:
- **API Health**: https://api.bottleplugug.com/api/health/
- **Main Site**: https://bottleplugug.com/api/health/

### Logs:
```bash
# View all logs
docker-compose -f docker-compose.prod.yml --env-file .env.prod logs

# View specific service logs
docker-compose -f docker-compose.prod.yml --env-file .env.prod logs nginx
docker-compose -f docker-compose.prod.yml --env-file .env.prod logs backend
```

## 🎉 Success!

Once everything is working, you'll have:
- ✅ Professional domain names
- ✅ SSL certificates (HTTPS)
- ✅ Automatic HTTP to HTTPS redirects
- ✅ Proper security headers
- ✅ Rate limiting protection

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure DNS records are correctly configured
4. Verify SSL certificates are properly installed

---

**Happy deploying! 🚀**

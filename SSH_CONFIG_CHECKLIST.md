# SSH Server Configuration Checklist

## Files to Check on Server

### 1. Environment Configuration
```bash
# Check production environment variables
cat /opt/bottleplug/.env.prod
ls -la /opt/bottleplug/.env*

# Check Docker environment
cat /opt/bottleplug/docker-compose.prod.yml
```

### 2. Django Settings
```bash
# Check Django settings files
cat /opt/bottleplug/backend/tanna_backend/settings.py
cat /opt/bottleplug/backend/tanna_backend/test_settings.py
ls -la /opt/bottleplug/backend/tanna_backend/*settings*
```

### 3. Firebase Configuration
```bash
# Check Firebase credentials
ls -la /opt/bottleplug/backend/firebase/
cat /opt/bottleplug/backend/firebase/*.json 2>/dev/null || echo "No Firebase files found"

# Check environment variables for Firebase
grep -r "FIREBASE" /opt/bottleplug/.env* 2>/dev/null || echo "No Firebase env vars found"
```

### 4. Database Configuration
```bash
# Check database setup
docker-compose -f /opt/bottleplug/docker-compose.prod.yml ps
docker-compose -f /opt/bottleplug/docker-compose.prod.yml logs backend | grep -i firebase
```

### 5. Deployment Scripts
```bash
# Check deployment configuration
ls -la /opt/bottleplug/scripts/
cat /opt/bottleplug/scripts/deploy.sh
```

### 6. Current Application Status
```bash
# Check running containers
docker ps
docker-compose -f /opt/bottleplug/docker-compose.prod.yml ps

# Check application logs
docker-compose -f /opt/bottleplug/docker-compose.prod.yml logs backend --tail=50
```

## Key Things to Look For

1. **Firebase Environment Variables**: Are they properly set in production?
2. **Django Settings**: Which settings file is being used in production?
3. **Database Configuration**: Is the database properly configured?
4. **Container Status**: Are all services running correctly?

## Commands to Run

```bash
# SSH into your server
ssh your_username@your_server_ip

# Navigate to application directory
cd /opt/bottleplug

# Check current status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs backend --tail=20

# Check environment files
ls -la .env*
cat .env.prod | grep -E "(FIREBASE|DATABASE|SECRET)"

# Check Django settings
cat backend/tanna_backend/settings.py | grep -A 10 -B 10 "Firebase"
```

## What to Share

Please share the output of these commands so I can help diagnose the CI/CD issues:

1. Environment variables (especially Firebase-related)
2. Django settings configuration
3. Docker container status
4. Application logs
5. Any error messages from the deployment

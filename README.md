# BottlePlug - E-commerce Platform

A complete e-commerce platform built with Vue.js frontend, Django backend, and admin dashboard.

## 🏗️ Architecture

This is a monorepo containing:

- **`web/`** - Vue.js frontend application
- **`backend/`** - Django REST API backend
- **`dashboard/`** - Admin dashboard
- **`docker-compose.yml`** - Development environment
- **`docker-compose.prod.yml`** - Production environment

## 🚀 Quick Start

### Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/bottleplug-monorepo.git
   cd bottleplug-monorepo
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment:**
   ```bash
   docker-compose up -d
   ```

4. **Access applications:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Dashboard: http://localhost:3001
   - Database Admin: http://localhost:5050

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed production deployment instructions.

## 📁 Project Structure

```
bottleplug-monorepo/
├── web/                    # Vue.js Frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── backend/                # Django Backend
│   ├── bottleplug/
│   ├── apps/
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/              # Admin Dashboard
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Development
├── docker-compose.prod.yml # Production
├── .github/workflows/      # CI/CD
├── DEPLOYMENT.md          # Deployment guide
└── README.md              # This file
```

## 🛠️ Technology Stack

### Frontend (web/)
- Vue.js 3
- Pinia (State Management)
- Vue Router
- Tailwind CSS
- Vite

### Backend (backend/)
- Django 4.2
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Firebase Authentication

### Dashboard (dashboard/)
- React
- Material-UI
- Chart.js

### Infrastructure
- Docker & Docker Compose
- Nginx (Reverse Proxy)
- Let's Encrypt (SSL)
- GitHub Actions (CI/CD)

## 🔧 Development Commands

### Frontend (web/)
```bash
cd web
npm install
npm run dev
npm run build
```

### Backend (backend/)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Dashboard (dashboard/)
```bash
cd dashboard
npm install
npm start
npm run build
```

### Docker Commands
```bash
# Development
docker-compose up -d
docker-compose logs -f

# Production
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔐 Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
POSTGRES_DB=bottleplug
POSTGRES_USER=bottleplug
POSTGRES_PASSWORD=your_password

# Django
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Flutterwave
FLUTTERWAVE_PUBLIC_KEY=your_public_key
FLUTTERWAVE_SECRET_KEY=your_secret_key
FLUTTERWAVE_ENCRYPTION_KEY=your_encryption_key

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

## 📊 Features

### E-commerce
- Product catalog with categories
- Shopping cart and checkout
- Order management
- Payment processing (Flutterwave)
- User authentication (Firebase)

### Events
- Event creation and management
- RSVP system
- Event payments
- Event tracking

### Admin Dashboard
- Product management
- Order tracking
- User management
- Analytics and reports

## 🚀 Deployment

### Automatic Deployment
The repository includes GitHub Actions for automatic deployment to Digital Ocean.

### Manual Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for step-by-step instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the deployment guide

---

**Built with ❤️ for modern e-commerce**
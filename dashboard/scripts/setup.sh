#!/bin/bash

# BottlePlug Dashboard Setup Script
echo "🍷 Welcome to BottlePlug Dashboard Setup!"
echo "=========================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v16 or higher."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) is installed"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if Firebase config exists
if [ ! -f "src/firebase/config.js" ]; then
    echo "❌ Firebase configuration file not found"
    exit 1
fi

# Check if Firebase config has placeholder values
if grep -q "your-api-key" src/firebase/config.js; then
    echo "⚠️  Firebase configuration needs to be updated"
    echo "Please follow the FIREBASE_SETUP.md guide to configure Firebase"
    echo ""
    echo "After configuring Firebase, run: npm run dev"
else
    echo "✅ Firebase configuration appears to be set up"
    echo ""
    echo "🚀 Starting development server..."
    npm run dev
fi

echo ""
echo "📚 Next steps:"
echo "1. Configure Firebase (see FIREBASE_SETUP.md)"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Open http://localhost:3000 in your browser"
echo "4. Register a new account and start using the dashboard"
echo ""
echo "🍷 Enjoy your BottlePlug Dashboard!" 
#!/bin/bash

# OpenClaw Mission Control Dashboard Setup Script

set -e

echo "🐝 OpenClaw Mission Control Dashboard Setup"
echo "=========================================="

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 18+ required. Found: $(node -v)"
    exit 1
fi

echo "✓ Node.js version: $(node -v)"

# Navigate to project directory
cd "$(dirname "$0")/my-app"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Setup environment
echo ""
echo "🔧 Setting up environment..."
if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo "✓ Created .env.local"
else
    echo "✓ .env.local already exists"
fi

# Check for Convex
echo ""
echo "☁️  Checking Convex setup..."
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found. Please install npm properly."
    exit 1
fi

echo ""
echo "⚠️  Important: You need to set up Convex:"
echo ""
echo "1. Go to https://convex.dev and create an account"
echo "2. Create a new project"
echo "3. Run: npx convex dev"
echo "4. Copy your Convex URL to .env.local:"
echo "   NEXT_PUBLIC_CONVEX_URL=https://your-url.convex.cloud"
echo ""

# Build project
echo "🔨 Building project..."
npm run build

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  cd dashboard/my-app"
echo "  npm run dev"
echo ""
echo "To deploy to production:"
echo "  npm run build"
echo "  # Upload dist/ folder to your hosting provider"
echo ""

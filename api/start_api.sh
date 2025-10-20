#!/bin/bash
# Quick start script for Whisp API

echo "========================================="
echo "Starting Whisp API"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and set your GEE_PROJECT before continuing!"
    echo "Press Ctrl+C to exit and edit .env, or Enter to continue..."
    read
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check GEE authentication
echo "Checking GEE authentication..."
python -c "import ee; ee.Initialize()" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  GEE not authenticated!"
    echo "Run: earthengine authenticate"
    echo ""
    echo "Do you want to authenticate now? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        earthengine authenticate
    fi
fi

echo ""
echo "========================================="
echo "Starting API server..."
echo "========================================="
echo ""
echo "API will be available at:"
echo "  - http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API
cd ..
python -m uvicorn api.app.main:app --host 0.0.0.0 --port 8000 --reload

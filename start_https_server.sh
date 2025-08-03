#!/bin/bash

# Sunrise Educational Centre - HTTPS Server Startup Script
# This script starts the Flask server with HTTPS enabled for WebRTC support

echo "🚀 Starting Sunrise Educational Centre Server with HTTPS..."
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import flask, flask_socketio, eventlet" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing required packages. Installing..."
    pip3 install flask flask-socketio eventlet requests
fi

# Check if SSL certificates exist
if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
    echo "⚠️  SSL certificates not found. Creating self-signed certificates..."
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ SSL certificates created successfully"
    else
        echo "❌ Failed to create SSL certificates. Please install OpenSSL."
        exit 1
    fi
else
    echo "✅ SSL certificates found"
fi

# Kill any existing processes on port 10000
echo "🔄 Stopping any existing server processes..."
pkill -f "python3 app.py" 2>/dev/null
sleep 2

# Start the server with HTTPS
echo "🌐 Starting server with HTTPS..."
echo "=================================================="
echo "✅ Server will be available at: https://localhost:10000"
echo "⚠️  Note: You may see a security warning in your browser."
echo "   Click 'Advanced' and then 'Proceed to localhost'"
echo "=================================================="

# Set environment variables and start server
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start the server
python3 app.py

echo ""
echo "�� Server stopped." 
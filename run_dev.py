#!/usr/bin/env python3
"""
Simple development server without SSL for testing
"""
from app import app, socketio

if __name__ == '__main__':
    print("🚀 Starting development server without SSL...")
    print("🌐 Access your app at: http://localhost:10000")
    print("⚠️  Note: WebRTC features will not work without HTTPS!")
    socketio.run(app, host='0.0.0.0', port=10000, debug=True) 
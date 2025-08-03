# WebRTC Camera/Microphone Access Fix

## 🚨 Issue: Camera/Microphone Access Problem

If you're seeing this error:
```
⚠️ Camera/Microphone Access Issue
Your browser does not support live video streaming
Issues detected:
    HTTPS connection required for camera access
    WebRTC not supported in this browser
```

## ✅ Solution: Enable HTTPS

The issue is that WebRTC (required for camera/microphone access) requires HTTPS. Here's how to fix it:

### Method 1: Quick Fix (Recommended)

1. **Stop the current server** (if running):
   ```bash
   pkill -f "python3 app.py"
   ```

2. **Start with HTTPS enabled**:
   ```bash
   FLASK_ENV=development python3 app.py
   ```

3. **Access your app at**: `https://localhost:10000` (note the `s` in `https`)

4. **Accept the security warning** in your browser:
   - Click "Advanced"
   - Click "Proceed to localhost (unsafe)"

### Method 2: Using the Startup Script

1. **Use the provided startup script**:
   ```bash
   ./start_https_server.sh
   ```

2. **Access your app at**: `https://localhost:10000`

### Method 3: Manual Setup

1. **Check SSL certificates exist**:
   ```bash
   ls -la *.pem
   ```

2. **If certificates don't exist, create them**:
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
   ```

3. **Start server with HTTPS**:
   ```bash
   FLASK_ENV=development python3 app.py
   ```

## 🔧 Troubleshooting

### If HTTPS still doesn't work:

1. **Check if server is running**:
   ```bash
   curl -k https://localhost:10000
   ```

2. **Verify SSL certificates**:
   ```bash
   python3 test_webrtc_setup.py
   ```

3. **Check port availability**:
   ```bash
   netstat -tlnp | grep :10000
   ```

### Browser-specific issues:

1. **Chrome/Edge**: 
   - Accept the security warning
   - Allow camera/microphone permissions

2. **Firefox**:
   - Click "Advanced" → "Accept the Risk and Continue"
   - Allow camera/microphone permissions

3. **Safari**:
   - Click "Show Details" → "visit this website"
   - Allow camera/microphone permissions

## 📋 Complete Setup Checklist

- [ ] Server running with `FLASK_ENV=development`
- [ ] SSL certificates exist (`cert.pem`, `key.pem`)
- [ ] Accessing via `https://localhost:10000` (not `http://`)
- [ ] Accepted security warning in browser
- [ ] Allowed camera/microphone permissions
- [ ] Using a modern browser (Chrome, Firefox, Edge, Safari)

## 🎯 Expected Result

After following these steps, you should be able to:
- Access the live class feature
- Use camera and microphone
- Join video calls
- Share screen (if supported)

## 🆘 Still Having Issues?

1. **Test the setup**:
   ```bash
   python3 test_webrtc_setup.py
   ```

2. **Check server logs** for any errors

3. **Try a different browser**

4. **Ensure no other apps are using camera/microphone**

## 📞 Alternative Solutions

If WebRTC still doesn't work, you can still use:
- YouTube video integration
- File uploads for sharing content
- Text-based communication in live classes

---

**Note**: This setup uses self-signed certificates for development. In production, use proper SSL certificates from a certificate authority. 
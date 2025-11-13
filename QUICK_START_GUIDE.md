# Garbage Classification App - Quick Start Guide

## Overview
This guide will help you quickly start the Garbage Classification application, including the Flutter mobile app and the FastAPI backend.

---

## Prerequisites
- ✅ Flutter SDK 3.38.0 (installed at `C:\src\flutter`)
- ✅ Conda environment `garbage-classification` (Python 3.10)
- ✅ Android Emulator configured
- ✅ All dependencies installed

---

## Step 1: Start the Android Emulator

### Option A: Using Flutter Command (Recommended)
```bash
# View available emulators
flutter emulators

# Launch the emulator
flutter emulators --launch Medium_Phone_API_36.1
```

### Option B: Using Android Studio
1. Open Android Studio
2. Click "Device Manager" (phone icon on the right side)
3. Click the play button next to your emulator

### Verify Emulator is Running
```bash
flutter devices
```
You should see the emulator listed with ID like `emulator-5554`.

---

## Step 2: Start the API Server

Open a **new terminal** window:

```bash
# Navigate to project directory
cd C:\Users\sophi\Desktop\yolov8-based-garbage-classification-app

# Activate conda environment
conda activate garbage-classification

# Start the API server
python api/main.py
```

The API will start on `http://0.0.0.0:8000`

### Verify API is Running
Open your browser and visit:
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

You should see a JSON response with GPU information:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "category_mapping_loaded": true,
  "gpu_available": true,
  "gpu_name": "NVIDIA GeForce RTX 4060 Laptop GPU",
  "device_in_use": "cuda:0"
}
```

---

## Step 3: Start the Flutter Application

Open a **new terminal** window (keep the API server running):

```bash
# Navigate to Flutter app directory
cd C:\Users\sophi\Desktop\yolov8-based-garbage-classification-app\mobile_app

# Add Flutter to PATH (if not permanent)
export PATH="/c/src/flutter/bin:$PATH"

# for windows
$env:PATH = "C:\src\flutter\bin;" + $env:PATH

# Run the Flutter app
flutter run
```

### Or specify the device:
```bash
flutter run -d emulator-5554
```

The app will compile and install on the emulator (first time takes 2-5 minutes).

---

## Using the Application

### App Features:
1. **Detection Tab** - Take photos or select from gallery to detect garbage
2. **Guide Tab** - Browse garbage classification guidelines
3. **About Tab** - View app information

### Flutter Development Commands:
While the app is running, you can use these commands in the terminal:

- `r` - Hot reload (quick update after code changes)
- `R` - Hot restart (full app restart)
- `q` - Quit and stop the app
- `h` - Show all available commands
- `c` - Clear the screen

---

## Stopping the Application

### Stop the Flutter App:
1. In the Flutter terminal, press `q`
2. Or press `Ctrl+C` to force quit

### Stop the API Server:
In the API terminal, press `Ctrl+C`

### Close the Emulator:
- Close the emulator window
- Or use: `adb -s emulator-5554 emu kill`

---

## Common Issues and Solutions

### Issue 1: Flutter command not found
**Solution:**
```bash
export PATH="/c/src/flutter/bin:$PATH"
```

To make it permanent, add to your `~/.bashrc` or `~/.bash_profile`:
```bash
echo 'export PATH="/c/src/flutter/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Issue 2: Emulator not detected
**Solution:**
```bash
# Check available devices
flutter devices

# Restart the emulator
flutter emulators --launch Medium_Phone_API_36.1
```

### Issue 3: API connection failed
**Problem:** App can't connect to API

**Solution:**
- The app is configured to use `http://10.0.2.2:8000` (Android emulator special address for localhost)
- Make sure API is running on `0.0.0.0:8000` not `127.0.0.1:8000`
- Check API logs for errors

### Issue 4: Conda environment not activated
**Solution:**
```bash
conda activate garbage-classification
```

### Issue 5: Permission denied errors in Flutter
**Solution:** Grant permissions in the emulator:
- Settings > Apps > Garbage Classification AI > Permissions
- Enable Camera and Storage permissions

### Issue 6: Slow inference on CPU
**Problem:** API is using CPU instead of GPU

**Solution:**
The API is now configured to automatically use your NVIDIA GeForce RTX 4060 GPU. Check the API logs on startup:
- Should see: "Using GPU: NVIDIA GeForce RTX 4060 Laptop GPU"
- Should see: "Model loaded successfully on device: cuda:0"

If GPU is not detected:
- Verify NVIDIA drivers are installed: `nvidia-smi`
- Check PyTorch CUDA version: `conda run -n garbage-classification python -c "import torch; print(torch.cuda.is_available())"`

---

## Quick Reference Commands

### Flutter Commands:
```bash
# Check Flutter installation
flutter doctor

# List available devices
flutter devices

# List available emulators
flutter emulators

# Run app (debug mode)
flutter run

# Run app (release mode)
flutter run --release

# Clean build cache
flutter clean

# Get dependencies
flutter pub get
```

### Conda Commands:
```bash
# List all environments
conda env list

# Activate environment
conda activate garbage-classification

# Deactivate environment
conda deactivate

# View installed packages
conda list
```

### Android Emulator Commands:
```bash
# List running emulators
adb devices

# Kill emulator
adb -s emulator-5554 emu kill

# Take screenshot
adb -s emulator-5554 exec-out screencap -p > screenshot.png
```

---

## Complete Startup Script

Save this as `start_app.sh` for quick startup:

```bash
#!/bin/bash

# Start API server in background
echo "Starting API server..."
cd C:/Users/sophi/Desktop/yolov8-based-garbage-classification-app
conda run -n garbage-classification python api/main.py &
API_PID=$!

# Wait for API to start
sleep 5

# Launch emulator
echo "Launching Android emulator..."
export PATH="/c/src/flutter/bin:$PATH"
flutter emulators --launch Medium_Phone_API_36.1 &

# Wait for emulator to boot
sleep 30

# Run Flutter app
echo "Starting Flutter app..."
cd mobile_app
flutter run

# Cleanup on exit
trap "kill $API_PID" EXIT
```

Make it executable:
```bash
chmod +x start_app.sh
```

Run it:
```bash
./start_app.sh
```

---

## Development Workflow

### 1. Morning Startup:
```bash
# Terminal 1: Start API
conda activate garbage-classification
cd C:/Users/sophi/Desktop/yolov8-based-garbage-classification-app
python api/main.py

# Terminal 2: Start Flutter
cd C:/Users/sophi/Desktop/yolov8-based-garbage-classification-app/mobile_app
flutter run
```

### 2. Making Changes:
- Edit code in your IDE
- Press `r` in Flutter terminal for hot reload
- Changes appear instantly without full restart

### 3. Testing:
- Use the app in the emulator
- Check API logs in API terminal
- Check Flutter logs in Flutter terminal

### 4. End of Day:
- Press `q` in Flutter terminal
- Press `Ctrl+C` in API terminal
- Close emulator window

---

## Project Structure Quick Reference

```
yolov8-based-garbage-classification-app/
├── api/
│   ├── main.py                    # API server entry point
│   └── test_client.py             # API testing script
│
├── mobile_app/                    # Flutter application
│   ├── lib/
│   │   ├── main.dart              # App entry point
│   │   ├── models/                # Data models
│   │   ├── services/              # API & image services
│   │   │   └── api_service.dart   # API endpoint: http://10.0.2.2:8000
│   │   ├── screens/               # UI pages
│   │   └── widgets/               # UI components
│   ├── android/                   # Android configuration
│   └── pubspec.yaml               # Flutter dependencies
│
├── models/                        # YOLOv8 model files
├── configs/                       # Configuration files
└── requirements.txt               # Python dependencies
```

---

## Troubleshooting Logs

### View Flutter Logs:
```bash
flutter logs
```

### View API Logs:
Check the terminal where API is running

### View Emulator Logs:
```bash
adb logcat | grep flutter
```

---

## Support

For issues or questions:
1. Check the logs in both terminals
2. Verify all services are running: `flutter devices` and check API at http://localhost:8000/health
3. Restart services if needed

---

**Last Updated:** 2025-11-13
**Flutter Version:** 3.38.0
**Python Version:** 3.10
**Conda Environment:** garbage-classification

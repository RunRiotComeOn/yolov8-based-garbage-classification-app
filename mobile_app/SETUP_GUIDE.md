# Flutter Mobile App Quick Setup Guide

## Environment Setup

### 1. Install Flutter SDK

#### Windows
```bash
# Download Flutter SDK
# https://flutter.dev/docs/get-started/install/windows

# Unzip to a directory
# Add to system environment variable PATH
```

#### macOS
```bash
# Install via Homebrew
brew install --cask flutter

# Or download manually
# https://flutter.dev/docs/get-started/install/macos
```

#### Linux
```bash
# Download Flutter SDK
cd ~
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.x.x-stable.tar.xz
tar xf flutter_linux_3.x.x-stable.tar.xz

# Add to PATH
echo 'export PATH="$PATH:`pwd`/flutter/bin"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Verify Flutter Installation
```bash
flutter doctor
```

Expected output:
```
✓ Flutter (Channel stable, 3.x.x)
✓ Android toolchain - develop for Android devices
✓ Xcode - develop for iOS and macOS (macOS only)
✓ Chrome - develop for the web
✓ Android Studio
✓ VS Code
✓ Connected device
```

### 3. Install Android Studio (Android Development)

1. Download Android Studio: https://developer.android.com/studio
2. Install Android SDK
3. Install Android SDK command-line tools
4. Configure Android emulator or connect a real device

### 4. Install Xcode (iOS Development, macOS only)

1. Install Xcode from the Mac App Store
2. Install command-line tools:
```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
```

3. Accept license agreement:
```bash
sudo xcodebuild -license accept
```

## Project Configuration

### 1. Navigate to Project Directory
```bash
cd /nas03/yixuh/garbage-classification/mobile_app
```

### 2. Install Dependencies
```bash
flutter pub get
```

### 3. Configure API Endpoint

#### Method 1: Local Network Testing (Recommended for Development)

1. Get server IP address:
```bash
# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

2. Edit `lib/services/api_service.dart`:
```dart
static const String defaultApiUrl = "http://192.168.1.10:8000";
// Replace with your server IP
```

#### Method 2: Use ngrok (Temporary Public Access)

1. Install ngrok on the API server:
```bash
# Download ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz

# Run ngrok
./ngrok http 8000
```

2. Copy the generated ngrok URL (e.g., https://xxxx.ngrok.io)

3. Update API endpoint:
```dart
static const String defaultApiUrl = "https://xxxx.ngrok.io";
```

#### Method 3: Cloud Server Deployment (Production)

1. Deploy API to a cloud server
2. Obtain public IP or domain name
3. Open port 8000 in the firewall
4. Update API endpoint

### 4. Configure Android Permissions

File: `android/app/src/main/AndroidManifest.xml` (already created)

Ensure the following permissions are included:
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.INTERNET" />
```

### 5. Configure iOS Permissions

File: `ios/Runner/Info.plist` (already created)

Ensure the following permission descriptions are included:
```xml
<key>NSCameraUsageDescription</key>
<string>Camera access is required to take photos of garbage for classification</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Photo library access is required to select garbage images for classification</string>
```

## Running the App

### 1. Connect Device or Start Emulator

#### Android Real Device
- Enable Developer Options
- Enable USB Debugging
- Connect device to computer
- Verify connection: `flutter devices`

#### Android Emulator
```bash
# Start emulator
flutter emulators
flutter emulators --launch <emulator_id>
```

#### iOS Simulator (macOS only)
```bash
open -a Simulator
```

### 2. Run the App

#### Debug Mode
```bash
flutter run
```

#### Release Mode
```bash
flutter run --release
```

### 3. Hot Reload (During Development)
- Press `r` to hot reload after code changes
- Press `R` to hot restart
- Press `q` to quit

## Building Release Versions

### Android APK

```bash
# Build APK
flutter build apk --release

# Output location
# build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle (Google Play)

```bash
flutter build appbundle --release

# Output location
# build/app/outputs/bundle/release/app-release.aab
```

### iOS IPA (macOS only)

```bash
# 1. Configure signing certificate
open ios/Runner.xcworkspace

# 2. Build
flutter build ios --release

# 3. Archive and export IPA in Xcode
```

## Test Checklist

### Functional Testing
- [ ] Camera capture works
- [ ] Photo gallery selection works
- [ ] API connection successful
- [ ] Detection results displayed correctly
- [ ] Bounding boxes drawn accurately
- [ ] Classification guide displayed
- [ ] Search functionality works
- [ ] Smooth page transitions

### Permission Testing
- [ ] First-time camera permission request
- [ ] First-time photo library permission request
- [ ] Prompt when permissions denied
- [ ] Navigation to permission settings

### Network Testing
- [ ] API responds correctly
- [ ] Network error prompts
- [ ] Timeout handling
- [ ] Retry mechanism

### UI Testing
- [ ] Displays correctly on different screen sizes
- [ ] Portrait/landscape orientation switching
- [ ] Loading animations
- [ ] Error messages

## Common Configuration Issues

### 1. Flutter SDK Not Found
```bash
# Set Flutter path
export PATH="$PATH:/path/to/flutter/bin"
```

### 2. Android Licenses Not Accepted
```bash
flutter doctor --android-licenses
```

### 3. CocoaPods Installation Failed (iOS)
```bash
cd ios
pod install
cd ..
```

### 4. Slow Gradle Downloads (Android)
Modify `android/build.gradle`:
```gradle
allprojects {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/public' }
        google()
        mavenCentral()
    }
}
```

### 5. API Connection Failed

#### Android Emulator Connecting to Local API
```dart
// Use 10.0.2.2 instead of localhost
static const String defaultApiUrl = "http://10.0.2.2:8000";
```

#### Android Real Device Connecting to LAN API
```dart
// Use actual server IP
static const String defaultApiUrl = "http://192.168.1.10:8000";
```

## API Server Configuration

### 1. Confirm API is Running
```bash
cd /nas03/yixuh/garbage-classification
conda activate garbage-classification
python api/main.py
```

### 2. Test API Connection
```bash
curl http://localhost:8000/health
```

### 3. Allow LAN Access
Ensure API listens on `0.0.0.0`:
```python
# api/main.py
uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

### 4. Configure Firewall
```bash
# Linux
sudo ufw allow 8000

# Or temporarily disable firewall for testing
sudo ufw disable
```

## Performance Optimization

### 1. Enable Code Obfuscation
```bash
flutter build apk --release --obfuscate --split-debug-info=build/debug-info
```

### 2. Reduce APK Size
```bash
# Use App Bundle
flutter build appbundle --release

# Or build per-ABI APKs
flutter build apk --release --split-per-abi
```

### 3. Optimize Image Assets
- Use WebP format
- Compress images
- Use appropriate resolutions

## Debugging Tips

### 1. View Logs
```bash
# Real-time logs
flutter logs

# Or during runtime
flutter run --verbose
```

### 2. Debug Network Requests
Add interceptor in `lib/services/api_service.dart`:
```dart
_dio.interceptors.add(LogInterceptor(
  requestBody: true,
  responseBody: true,
));
```

### 3. Performance Profiling
```bash
flutter run --profile
```

### 4. Memory Leak Detection
```bash
flutter run --enable-checked-mode
```

## Publishing to App Stores

### Google Play Store
1. Create a Google Play developer account
2. Create an app
3. Build App Bundle
4. Upload and fill in app details
5. Submit for review

### Apple App Store
1. Create an Apple developer account
2. Create app in App Store Connect
3. Configure certificates and provisioning profiles
4. Build and archive
5. Upload IPA
6. Submit for review

## Support & Help

### Official Flutter Documentation
- https://flutter.dev/docs

### Frequently Asked Questions
- https://flutter.dev/docs/resources/faq

### Community Support
- Stack Overflow: https://stackoverflow.com/questions/tagged/flutter
- Flutter Dev Discord: https://discord.gg/flutter
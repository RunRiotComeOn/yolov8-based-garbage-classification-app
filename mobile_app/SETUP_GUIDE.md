# Flutter 移动应用快速配置指南

## 环境准备

### 1. 安装Flutter SDK

#### Windows
```bash
# 下载Flutter SDK
# https://flutter.dev/docs/get-started/install/windows

# 解压到目录
# 添加到系统环境变量 PATH
```

#### macOS
```bash
# 使用Homebrew安装
brew install --cask flutter

# 或手动下载
# https://flutter.dev/docs/get-started/install/macos
```

#### Linux
```bash
# 下载Flutter SDK
cd ~
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.x.x-stable.tar.xz
tar xf flutter_linux_3.x.x-stable.tar.xz

# 添加到PATH
echo 'export PATH="$PATH:`pwd`/flutter/bin"' >> ~/.bashrc
source ~/.bashrc
```

### 2. 验证Flutter安装
```bash
flutter doctor
```

输出应显示:
```
✓ Flutter (Channel stable, 3.x.x)
✓ Android toolchain - develop for Android devices
✓ Xcode - develop for iOS and macOS (仅macOS)
✓ Chrome - develop for the web
✓ Android Studio
✓ VS Code
✓ Connected device
```

### 3. 安装Android Studio (Android开发)

1. 下载Android Studio: https://developer.android.com/studio
2. 安装Android SDK
3. 安装Android SDK命令行工具
4. 配置Android模拟器或连接真机

### 4. 安装Xcode (iOS开发, 仅macOS)

1. 从Mac App Store安装Xcode
2. 安装命令行工具:
```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
```

3. 同意许可协议:
```bash
sudo xcodebuild -license accept
```

## 项目配置

### 1. 进入项目目录
```bash
cd /nas03/yixuh/garbage-classification/mobile_app
```

### 2. 安装依赖
```bash
flutter pub get
```

### 3. 配置API地址

#### 方法一: 局域网测试(推荐用于开发)

1. 获取服务器IP地址:
```bash
# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

2. 编辑 `lib/services/api_service.dart`:
```dart
static const String defaultApiUrl = "http://192.168.1.10:8000";
// 替换为你的服务器IP
```

#### 方法二: 使用ngrok(临时公网访问)

1. 在API服务器上安装ngrok:
```bash
# 下载ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz

# 运行ngrok
./ngrok http 8000
```

2. 复制ngrok生成的URL (例如: https://xxxx.ngrok.io)

3. 更新API地址:
```dart
static const String defaultApiUrl = "https://xxxx.ngrok.io";
```

#### 方法三: 云服务器部署(生产环境)

1. 将API部署到云服务器
2. 获取公网IP或域名
3. 配置防火墙开放8000端口
4. 更新API地址

### 4. 配置Android权限

文件: `android/app/src/main/AndroidManifest.xml` (已创建)

确认包含以下权限:
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.INTERNET" />
```

### 5. 配置iOS权限

文件: `ios/Runner/Info.plist` (已创建)

确认包含以下权限说明:
```xml
<key>NSCameraUsageDescription</key>
<string>需要使用相机拍摄垃圾照片进行识别</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>需要访问相册以选择垃圾照片进行识别</string>
```

## 运行应用

### 1. 连接设备或启动模拟器

#### Android真机
- 开启开发者选项
- 启用USB调试
- 连接设备到电脑
- 验证连接: `flutter devices`

#### Android模拟器
```bash
# 启动模拟器
flutter emulators
flutter emulators --launch <emulator_id>
```

#### iOS模拟器 (仅macOS)
```bash
open -a Simulator
```

### 2. 运行应用

#### 调试模式
```bash
flutter run
```

#### 发布模式
```bash
flutter run --release
```

### 3. 热重载(开发时)
- 修改代码后按 `r` 热重载
- 按 `R` 热重启
- 按 `q` 退出

## 构建发布版本

### Android APK

```bash
# 构建APK
flutter build apk --release

# 输出位置
# build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle (Google Play)

```bash
flutter build appbundle --release

# 输出位置
# build/app/outputs/bundle/release/app-release.aab
```

### iOS IPA (仅macOS)

```bash
# 1. 配置签名证书
open ios/Runner.xcworkspace

# 2. 构建
flutter build ios --release

# 3. 在Xcode中归档和导出IPA
```

## 测试清单

### 功能测试
- [ ] 拍照功能正常
- [ ] 相册选择正常
- [ ] API连接成功
- [ ] 检测结果显示正常
- [ ] 边界框绘制正确
- [ ] 分类指南显示正常
- [ ] 搜索功能正常
- [ ] 页面切换流畅

### 权限测试
- [ ] 首次请求相机权限
- [ ] 首次请求相册权限
- [ ] 权限拒绝后的提示
- [ ] 权限设置跳转

### 网络测试
- [ ] API正常响应
- [ ] 网络错误提示
- [ ] 超时处理
- [ ] 重试机制

### UI测试
- [ ] 不同屏幕尺寸显示正常
- [ ] 横竖屏切换
- [ ] 加载动画
- [ ] 错误提示

## 常见配置问题

### 1. Flutter SDK未找到
```bash
# 设置Flutter路径
export PATH="$PATH:/path/to/flutter/bin"
```

### 2. Android许可未接受
```bash
flutter doctor --android-licenses
```

### 3. CocoaPods安装失败 (iOS)
```bash
cd ios
pod install
cd ..
```

### 4. Gradle下载慢 (Android)
修改 `android/build.gradle`:
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

### 5. API连接失败

#### Android模拟器连接本地API
```dart
// 使用10.0.2.2代替localhost
static const String defaultApiUrl = "http://10.0.2.2:8000";
```

#### Android真机连接局域网API
```dart
// 使用服务器实际IP
static const String defaultApiUrl = "http://192.168.1.10:8000";
```

## API服务器配置

### 1. 确认API正在运行
```bash
cd /nas03/yixuh/garbage-classification
conda activate garbage-classification
python api/main.py
```

### 2. 测试API连接
```bash
curl http://localhost:8000/health
```

### 3. 允许局域网访问
确保API监听 `0.0.0.0`:
```python
# api/main.py
uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

### 4. 配置防火墙
```bash
# Linux
sudo ufw allow 8000

# 或临时关闭防火墙测试
sudo ufw disable
```

## 性能优化

### 1. 启用代码压缩
```bash
flutter build apk --release --obfuscate --split-debug-info=build/debug-info
```

### 2. 减小APK大小
```bash
# 使用App Bundle
flutter build appbundle --release

# 或构建特定架构的APK
flutter build apk --release --split-per-abi
```

### 3. 优化图片资源
- 使用WebP格式
- 压缩图片
- 使用适当的分辨率

## 调试技巧

### 1. 查看日志
```bash
# 实时查看日志
flutter logs

# 或在运行时查看
flutter run --verbose
```

### 2. 调试网络请求
在 `lib/services/api_service.dart` 中添加拦截器:
```dart
_dio.interceptors.add(LogInterceptor(
  requestBody: true,
  responseBody: true,
));
```

### 3. 性能分析
```bash
flutter run --profile
```

### 4. 内存泄漏检测
```bash
flutter run --enable-checked-mode
```

## 发布到应用商店

### Google Play Store
1. 创建Google Play开发者账号
2. 创建应用
3. 构建App Bundle
4. 上传并填写应用信息
5. 提交审核

### Apple App Store
1. 创建Apple开发者账号
2. 在App Store Connect创建应用
3. 配置证书和描述文件
4. 构建并归档
5. 上传IPA
6. 提交审核

## 支持与帮助

### Flutter官方文档
- https://flutter.dev/docs

### 常见问题
- https://flutter.dev/docs/resources/faq

### 社区支持
- Stack Overflow: https://stackoverflow.com/questions/tagged/flutter
- Flutter Dev Discord: https://discord.gg/flutter

## 下一步

1. ✅ 完成环境配置
2. ✅ 配置API地址
3. ✅ 运行应用测试
4. ✅ 进行功能测试
5. ⬜ 根据需求定制UI
6. ⬜ 添加额外功能
7. ⬜ 构建发布版本
8. ⬜ 部署到生产环境

祝你开发顺利! 🚀

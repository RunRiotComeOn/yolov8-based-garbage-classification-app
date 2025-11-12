# 项目结构说明

## 目录结构

```
mobile_app/
│
├── lib/                          # 应用源代码
│   ├── models/                   # 数据模型
│   │   ├── detection.dart        # 检测结果数据模型
│   │   └── garbage_guide.dart    # 垃圾分类指南数据模型
│   │
│   ├── services/                 # 业务逻辑服务层
│   │   ├── api_service.dart      # API网络请求服务
│   │   ├── guide_service.dart    # 垃圾分类指南服务
│   │   └── image_picker_service.dart  # 图片选择服务
│   │
│   ├── screens/                  # UI页面
│   │   ├── home_screen.dart      # 主页面(包含底部导航)
│   │   ├── detection_screen.dart # 垃圾检测页面
│   │   └── guide_screen.dart     # 分类指南页面
│   │
│   ├── widgets/                  # 可复用UI组件
│   │   └── detection_painter.dart # 边界框绘制组件
│   │
│   └── main.dart                 # 应用入口
│
├── android/                      # Android平台配置
│   └── app/
│       └── src/
│           └── main/
│               └── AndroidManifest.xml  # Android权限配置
│
├── ios/                          # iOS平台配置
│   └── Runner/
│       └── Info.plist            # iOS权限配置
│
├── assets/                       # 资源文件
│   ├── data/                     # 数据文件
│   └── images/                   # 图片资源
│
├── pubspec.yaml                  # Flutter项目配置和依赖
├── analysis_options.yaml         # Dart代码分析配置
├── .gitignore                    # Git忽略文件配置
│
├── README.md                     # 项目说明文档
├── SETUP_GUIDE.md               # 配置指南
├── PROJECT_STRUCTURE.md         # 项目结构说明(本文件)
└── test_api.sh                  # API测试脚本
```

## 核心文件说明

### 应用入口
- **lib/main.dart**: 应用入口文件,配置主题和路由

### 数据模型层 (Models)
- **lib/models/detection.dart**:
  - `Detection`: 单个检测结果模型
  - `DetectionResponse`: API响应模型

- **lib/models/garbage_guide.dart**:
  - `GarbageCategory`: 垃圾分类类别模型
  - `GarbageItem`: 具体垃圾物品模型

### 服务层 (Services)
- **lib/services/api_service.dart**:
  - `GarbageDetectorService`: API通信服务
  - 方法: `detectGarbage()`, `checkHealth()`, `getCategories()`

- **lib/services/guide_service.dart**:
  - `GuideService`: 垃圾分类指南数据服务
  - 方法: `getAllCategories()`, `getAllItems()`, `searchItems()`

- **lib/services/image_picker_service.dart**:
  - `ImagePickerService`: 图片选择服务
  - 方法: `pickFromCamera()`, `pickFromGallery()`

### UI页面层 (Screens)
- **lib/screens/home_screen.dart**:
  - `HomeScreen`: 主页面,包含底部导航栏
  - `AboutScreen`: 关于页面

- **lib/screens/detection_screen.dart**:
  - `DetectionScreen`: 垃圾检测主界面
  - 功能: 拍照、选图、显示结果、绘制边界框

- **lib/screens/guide_screen.dart**:
  - `GuideScreen`: 垃圾分类指南页面
  - 功能: 展示分类信息、搜索功能

### UI组件层 (Widgets)
- **lib/widgets/detection_painter.dart**:
  - `DetectionPainter`: 自定义绘制器,用于绘制边界框
  - `DetectionOverlay`: 检测结果覆盖层组件

## 数据流

```
用户操作
   ↓
UI层 (Screens/Widgets)
   ↓
服务层 (Services)
   ↓
API/数据源
   ↓
数据模型 (Models)
   ↓
UI更新
```

## 依赖关系

```
main.dart
   └── home_screen.dart
       ├── detection_screen.dart
       │   ├── api_service.dart → detection.dart
       │   ├── image_picker_service.dart
       │   └── detection_painter.dart → detection.dart
       │
       ├── guide_screen.dart
       │   └── guide_service.dart → garbage_guide.dart
       │
       └── about_screen.dart
```

## 状态管理

当前使用 **StatefulWidget** 进行局部状态管理:
- `DetectionScreen`: 管理图片、检测结果、加载状态
- `GuideScreen`: 管理搜索状态和结果

未来可考虑使用 Provider、Riverpod 或 Bloc 进行全局状态管理。

## 路由配置

使用 Material App 默认路由:
- 底部导航栏切换页面
- Dialog弹窗显示详细信息

## 主题配置

在 `main.dart` 中配置:
- 主色调: Green (绿色)
- Material Design 3
- 自定义AppBar、Card、Button样式

## API集成

### 端点
- `POST /v1/detect_trash`: 垃圾检测
- `GET /health`: 健康检查
- `GET /v1/categories`: 获取分类信息
- `GET /docs`: API文档

### 请求格式
- Content-Type: `multipart/form-data`
- 参数: `image` (图片文件)

### 响应格式
```json
{
  "status": "success",
  "detection_count": 2,
  "detections": [...],
  "inference_time_ms": 45.23
}
```

## 权限管理

### Android (AndroidManifest.xml)
- CAMERA: 相机拍照
- READ_EXTERNAL_STORAGE: 读取相册
- WRITE_EXTERNAL_STORAGE: 保存图片
- INTERNET: 网络请求
- ACCESS_NETWORK_STATE: 网络状态

### iOS (Info.plist)
- NSCameraUsageDescription: 相机使用说明
- NSPhotoLibraryUsageDescription: 相册访问说明
- NSPhotoLibraryAddUsageDescription: 保存到相册

## 代码规范

### 命名规范
- 文件名: `snake_case.dart`
- 类名: `PascalCase`
- 变量/方法: `camelCase`
- 常量: `UPPER_SNAKE_CASE`
- 私有成员: `_leadingUnderscore`

### 代码组织
1. Import语句
2. 常量定义
3. 类定义
4. 构造函数
5. 生命周期方法
6. 业务方法
7. UI构建方法
8. 私有方法

### 注释规范
- 使用 `///` 文档注释
- 类和公共方法必须有文档注释
- 复杂逻辑添加行内注释

## 性能优化

### 已实现
- 图片压缩 (maxWidth: 1920, quality: 85)
- 网络超时设置 (30秒)
- 状态管理优化
- Widget复用

### 待优化
- 图片缓存
- 列表虚拟滚动
- 路由懒加载
- 资源预加载

## 测试策略

### 单元测试
- Models: 数据模型序列化/反序列化
- Services: API调用、数据处理逻辑

### Widget测试
- 页面渲染
- 用户交互
- 状态变化

### 集成测试
- 完整流程测试
- API集成测试

## 构建配置

### Debug模式
```bash
flutter run
```
- 包含调试信息
- 支持热重载
- 文件较大

### Release模式
```bash
flutter build apk --release
```
- 代码混淆
- 资源优化
- 文件压缩

### Profile模式
```bash
flutter run --profile
```
- 性能分析
- 保留部分调试信息

## 版本管理

### 版本号格式
`major.minor.patch+build`

示例: `1.0.0+1`
- major: 主版本(不兼容的API变更)
- minor: 次版本(新增功能,向后兼容)
- patch: 补丁版本(bug修复)
- build: 构建号(递增)

### 更新版本
编辑 `pubspec.yaml`:
```yaml
version: 1.0.0+1
```

## 扩展功能规划

### 短期
- [ ] 离线缓存
- [ ] 历史记录
- [ ] 分享功能
- [ ] 深色模式

### 中期
- [ ] 多语言支持
- [ ] 离线模型
- [ ] 批量处理
- [ ] 统计分析

### 长期
- [ ] 环保积分系统
- [ ] 社区功能
- [ ] 回收点地图
- [ ] AI学习优化

## 维护建议

### 日常维护
- 定期更新依赖包
- 修复已知bug
- 优化性能
- 更新文档

### 版本发布
1. 功能开发和测试
2. 更新版本号
3. 生成CHANGELOG
4. 构建发布版本
5. 上传应用商店
6. 发布更新公告

### 监控指标
- 崩溃率
- API响应时间
- 用户活跃度
- 功能使用率

## 相关资源

- [Flutter官方文档](https://flutter.dev/docs)
- [Dart语言文档](https://dart.dev/guides)
- [Material Design](https://material.io/design)
- [API后端文档](../README.md)

---

**最后更新**: 2025-11-12

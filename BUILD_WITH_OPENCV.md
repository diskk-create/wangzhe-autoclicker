# 王者荣耀自动点击器 - OpenCV集成指南

## 当前状态

### ✅ 已完成功能
1. **Android原生悬浮窗** - 真正的悬浮窗，可在其他应用上显示
2. **11步自动点击** - 完整的王者荣耀游戏流程
3. **智能点击策略** - 找图 > 找字 > 坐标点击（兜底）
4. **三层点击实现** - ROOT优先、无障碍服务备用、ADB调试兜底
5. **实时状态显示** - 状态、步骤、日志实时更新
6. **基础图像识别框架** - 预留OpenCV接口

### ⚠️ 需要OpenCV的增强功能
目前图像识别是**模拟版本**，需要集成OpenCV实现真正的图像识别：
- **找图功能** - 基于模板匹配
- **找字功能** - 基于文字识别（OCR）
- **颜色匹配** - 更准确的颜色识别

## OpenCV集成步骤

### 方法一：使用OpenCV Android SDK（推荐）

1. **下载OpenCV Android SDK**
   - 访问：https://opencv.org/releases/
   - 下载Android版本（如OpenCV-4.8.0-android-sdk.zip）

2. **导入OpenCV模块**
   ```bash
   # 解压OpenCV SDK
   unzip OpenCV-4.8.0-android-sdk.zip
   
   # 将sdk/java目录复制到项目
   cp -r OpenCV-android-sdk/sdk/java app/libs/opencv
   ```

3. **修改app/build.gradle**
   ```gradle
   android {
       // 添加OpenCV库目录
       sourceSets {
           main {
               jniLibs.srcDirs = ['libs/opencv/libs']
           }
       }
   }
   
   dependencies {
       // OpenCV依赖
       implementation project(':opencv')
   }
   ```

4. **初始化OpenCV**
   在MainActivity中添加：
   ```kotlin
   class MainActivity : AppCompatActivity() {
       override fun onCreate(savedInstanceState: Bundle?) {
           super.onCreate(savedInstanceState)
           
           // 加载OpenCV库
           if (!OpenCVLoader.initDebug()) {
               Log.e("OpenCV", "无法加载OpenCV库")
           } else {
               Log.d("OpenCV", "OpenCV库加载成功")
           }
       }
   }
   ```

### 方法二：使用预编译的OpenCV库

1. **添加依赖到build.gradle**
   ```gradle
   dependencies {
       implementation 'com.quickbirdstudios:opencv:4.8.0'
   }
   ```

2. **在Application中初始化**
   ```kotlin
   class MyApp : Application() {
       override fun onCreate() {
           super.onCreate()
           OpenCVLoader.initDebug()
       }
   }
   ```

## 图像识别功能升级

### 1. 真正的模板匹配
```kotlin
class RealImageRecognizer(private val context: Context) {
    private val opencv = OpenCVLoader.initDebug()
    
    fun findImageReal(templateName: String, screenWidth: Int, screenHeight: Int): RecognitionResult {
        // 1. 截图
        val screenshot = takeScreenshot()
        
        // 2. 加载模板图片
        val template = loadTemplate(templateName)
        
        // 3. 模板匹配
        val result = matchTemplate(screenshot, template)
        
        // 4. 找到最佳匹配
        val (x, y, confidence) = findBestMatch(result)
        
        return RecognitionResult(
            success = confidence >= 90,
            confidence = confidence,
            x = x,
            y = y,
            message = if (confidence >= 90) "找到${templateName}" else "未找到${templateName}"
        )
    }
}
```

### 2. 真正的文字识别
```kotlin
fun findTextReal(text: String, screenWidth: Int, screenHeight: Int): RecognitionResult {
    // 1. 截图
    val screenshot = takeScreenshot()
    
    // 2. 使用Tesseract OCR
    val tess = TessBaseAPI()
    tess.init("/path/to/tessdata", "chi_sim") // 中文识别
    
    // 3. 设置图像
    tess.setImage(screenshot)
    
    // 4. 识别文字
    val recognizedText = tess.utF8Text
    
    // 5. 查找目标文字
    if (recognizedText.contains(text)) {
        // 获取文字位置
        val (x, y) = getTextPosition(text, recognizedText)
        return RecognitionResult(true, 95, x, y, "找到文字: $text")
    }
    
    return RecognitionResult(false, 0, message = "未找到文字: $text")
}
```

## 构建脚本

### 1. 基础构建（无OpenCV）
```bash
cd wangzhe_autoclicker_native
.\build.bat
```

### 2. 带OpenCV的构建（需要先集成OpenCV）
```bash
cd wangzhe_autoclicker_native
# 先下载OpenCV库
# 然后修改build.gradle
# 最后构建
.\gradlew.bat assembleDebug
```

## 功能测试

### 测试图像识别
1. 安装APK
2. 授予悬浮窗权限
3. 点击悬浮球展开菜单
4. 点击"🖼️ Test Image"按钮
5. 查看日志输出

### 测试智能点击
1. 启动王者荣耀游戏
2. 开启悬浮窗服务
3. 点击"▶ Start"按钮
4. 观察自动执行11步流程
5. 查看每一步使用的策略（找图/找字/坐标）

## 性能优化建议

### 1. 图像识别优化
```kotlin
// 缓存模板图片
private val templateCache = mutableMapOf<String, Bitmap>()

// 预加载模板
fun preloadTemplates() {
    buttonTemplates.keys.forEach { name ->
        templateCache[name] = loadTemplate(name)
    }
}

// 使用缓存
fun findImageCached(name: String): RecognitionResult {
    val template = templateCache[name] ?: return RecognitionResult(false, 0)
    // ... 使用缓存的模板进行匹配
}
```

### 2. 多线程处理
```kotlin
private val recognitionExecutor = Executors.newFixedThreadPool(4)

fun findImageAsync(name: String, callback: (RecognitionResult) -> Unit) {
    recognitionExecutor.submit {
        val result = findImage(name)
        mainHandler.post { callback(result) }
    }
}
```

### 3. 分辨率适配优化
```kotlin
// 动态计算模板缩放
fun getScaledTemplate(name: String, screenWidth: Int, screenHeight: Int): Bitmap {
    val original = templateCache[name] ?: return null
    val scaleX = screenWidth.toFloat() / BASE_WIDTH
    val scaleY = screenHeight.toFloat() / BASE_HEIGHT
    
    return Bitmap.createScaledBitmap(
        original,
        (original.width * scaleX).toInt(),
        (original.height * scaleY).toInt(),
        true
    )
}
```

## 注意事项

1. **OpenCV库大小** - OpenCV库较大（约60MB），会增加APK体积
2. **性能考虑** - 图像识别需要CPU计算，可能影响性能
3. **内存使用** - 截图和模板匹配需要内存
4. **权限要求** - 需要屏幕截图权限
5. **兼容性** - 不同Android版本可能行为不同

## 备用方案

如果OpenCV集成太复杂，可以先使用当前版本：

1. **当前版本**：模拟识别 + 坐标点击（可用）
2. **中级版本**：颜色匹配 + 坐标点击
3. **完整版本**：OpenCV模板匹配 + Tesseract OCR

**建议**：先使用当前版本测试基础功能，确认悬浮窗和点击正常工作，再逐步集成OpenCV。
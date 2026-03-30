# WangZhe Auto Clicker - 本地测试环境

## 环境配置

### Python版本
- **Python 3.11.9** - 用于本地测试（兼容Kivy）
- 安装位置: `C:\Python311\`
- 不影响系统现有的Python 3.14

### 已安装的依赖
- Kivy 2.3.1
- kivy-deps.sdl2 0.8.0
- kivy-deps.glew 0.3.1
- kivy-deps.angle 0.4.0
- Pillow 10.4.0
- pywin32 311

## 如何运行

### 方法1: 使用批处理文件
```cmd
run_local.bat
```

### 方法2: 直接运行
```cmd
C:\Python311\python.exe main.py
```

### 方法3: 使用Python 3.11虚拟环境
```cmd
C:\Python311\python.exe -m venv venv
venv\Scripts\activate
pip install kivy[base]
python main.py
```

## 应用功能

### 悬浮球UI
- **悬浮球**: 蓝色圆形按钮，可拖动
- **展开菜单**: 点击悬浮球展开功能菜单
- **收起菜单**: 再次点击或点击外部收起

### 功能按钮
- **▶ Start**: 开始自动点击循环
- **⏸ Stop**: 停止自动点击
- **🔄 Test**: 测试单次点击
- **✕ Exit**: 退出应用

### 状态显示
- 🔵 蓝色 = 就绪状态
- 🟢 绿色 = 运行中/菜单展开
- 🟡 黄色 = 已停止

## 测试流程

### 1. 本地测试
1. 运行 `run_local.bat`
2. 测试悬浮球UI
3. 测试拖动功能
4. 测试展开/收起菜单
5. 测试按钮功能

### 2. 模拟器测试
```cmd
# 连接模拟器
adb connect 127.0.0.1:21503

# 运行测试脚本
C:\Python311\python.exe test_local.py
```

### 3. APK构建
本地测试通过后，推送到GitHub构建APK

## 文件说明

| 文件 | 说明 |
|------|------|
| main.py | 悬浮球版本主程序 |
| main_v336.py | v3.3.6备份（完整功能版）|
| test_local.py | 本地ADB测试脚本 |
| run_local.bat | 本地运行批处理 |
| buildozer.spec | Android构建配置 |

## 下一步

1. ✅ 本地环境已配置
2. ⏳ 测试悬浮球UI
3. ⏳ 测试点击功能
4. ⏳ 测试循环运行
5. ⏳ 修复问题
6. ⏳ 构建APK
7. ⏳ 真机测试

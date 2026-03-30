# Windows环境打包APK教程

## 方法1: 使用WSL（推荐）⭐⭐⭐⭐⭐

### 步骤1: 启用WSL

在Windows PowerShell（管理员）中运行：

```powershell
# 启用WSL
wsl --install -d Ubuntu-20.04

# 如果已安装，启动WSL
wsl
```

### 步骤2: 在WSL中配置环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y git zip unzip openjdk-11-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev automake

# 安装Python
sudo apt install python3 python3-pip -y

# 安装Buildozer
pip3 install buildozer cython==0.29.33

# 安装其他依赖
pip3 install kivy opencv-python
```

### 步骤3: 进入项目目录

```bash
# 进入Windows文件系统
cd /mnt/c/Users/Administrator/.openclaw/workspace/王者荣耀自动点击器_APK

# 或者复制项目到WSL中（更快）
cp -r /mnt/c/Users/Administrator/.openclaw/workspace/王者荣耀自动点击器_APK ~/
cd ~/王者荣耀自动点击器_APK
```

### 步骤4: 复制模板图片

```bash
# 从备份目录复制模板图片
cp ../备份1/template_*.png templates/
cp ../备份1/text_template_*.png templates/
```

### 步骤5: 打包APK

```bash
# 首次打包（需要下载SDK/NDK，约30-60分钟）
buildozer android debug

# 后续打包（约5-10分钟）
buildozer android debug
```

### 步骤6: 获取APK

```bash
# APK位置
ls -lh bin/

# 复制到Windows
cp bin/王者荣耀自动点击器-1.0.0-arm64-v8a-debug.apk /mnt/c/Users/Administrator/Desktop/
```

---

## 方法2: 使用云服务器（最简单）⭐⭐⭐⭐

### 推荐: GitHub Actions

**步骤1: 上传到GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/wangzhe-autoclicker.git
git push -u origin main
```

**步骤2: 创建.github/workflows/build.yml**

```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.9
      uses: actions/setup-python@v3
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install buildozer cython==0.29.33
        sudo apt-get install -y git zip unzip openjdk-11-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev automake

    - name: Build with Buildozer
      run: buildozer android debug

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: app-debug
        path: bin/*.apk
```

**步骤3: 触发构建**

推送代码到GitHub，自动构建APK。

**步骤4: 下载APK**

在GitHub Actions页面下载构建好的APK。

---

## 方法3: 使用Docker（最稳定）⭐⭐⭐⭐

### 步骤1: 安装Docker Desktop

下载并安装: https://www.docker.com/products/docker-desktop

### 步骤2: 创建Dockerfile

```dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git \
    zip \
    unzip \
    openjdk-11-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install buildozer cython==0.29.33 kivy opencv-python

WORKDIR /app
COPY . .

CMD ["buildozer", "android", "debug"]
```

### 步骤3: 构建并运行

```bash
# 构建镜像
docker build -t wangzhe-builder .

# 运行容器
docker run -v $(pwd)/bin:/app/bin wangzhe-builder

# APK将出现在bin目录
```

---

## 方法4: 使用在线服务

### 选项A: Replit

1. 访问 https://replit.com
2. 创建新项目（Python）
3. 上传项目文件
4. 在Shell中运行打包命令

### 选项B: Gitpod

1. 访问 https://gitpod.io
2. 连接GitHub仓库
3. 自动启动开发环境
4. 运行打包命令

---

## 常见问题

### 问题1: 内存不足

**解决方案:**
```bash
# 增加WSL内存
# 在Windows中创建 %USERPROFILE%\.wslconfig

[wsl2]
memory=8GB
processors=4
```

### 问题2: 网络问题

**解决方案:**
```bash
# 使用国内镜像
export GRADLE_OPTS="-Dorg.gradle.jvmargs=-Xmx2048m"
```

### 问题3: 权限问题

**解决方案:**
```bash
# 修复权限
chmod +x build_apk.sh
sudo chown -R $USER:$USER .
```

---

## 预计时间

| 方法 | 首次打包 | 后续打包 | 难度 |
|------|---------|---------|------|
| WSL | 30-60分钟 | 5-10分钟 | ⭐⭐⭐ |
| GitHub Actions | 20-40分钟 | 5-10分钟 | ⭐⭐ |
| Docker | 40-80分钟 | 5-10分钟 | ⭐⭐⭐⭐ |
| 在线服务 | 30-50分钟 | 5-10分钟 | ⭐ |

---

## 推荐方案

**如果你是新手:**
→ 使用 **GitHub Actions**（最简单，无需本地环境）

**如果你有经验:**
→ 使用 **WSL**（最灵活，可在Windows中直接操作）

**如果你追求稳定:**
→ 使用 **Docker**（环境隔离，不会污染系统）

---

## 下一步

1. 选择一种方法
2. 按照步骤操作
3. 获取APK
4. 安装到Android设备
5. 开始使用！
# 自动推送到GitHub脚本
# 支持多种推送方式

$ProjectDir = "C:\Users\Administrator\.openclaw\workspace\wangzhe_autoclicker_v3"
$GitHubRepo = "https://github.com/diskk-create/wangzhe-autoclicker.git"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "王者荣耀自动点击器 v3.0 - 自动推送到GitHub" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# 进入项目目录
Set-Location $ProjectDir
Write-Host "[信息] 工作目录: $ProjectDir" -ForegroundColor Yellow

# 检查Git状态
Write-Host ""
Write-Host "[1/5] 检查Git状态..." -ForegroundColor Yellow
$gitStatus = git status --short
if ($gitStatus) {
    Write-Host "[警告] 有未提交的文件，正在添加..." -ForegroundColor Yellow
    git add .
    git commit -m "添加推送说明文档"
}

# 显示当前提交
Write-Host ""
Write-Host "[2/5] 当前提交:" -ForegroundColor Yellow
git log --oneline -1

# 检查远程仓库
Write-Host ""
Write-Host "[3/5] 检查远程仓库..." -ForegroundColor Yellow
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "[成功] 远程仓库: $remote" -ForegroundColor Green
} else {
    Write-Host "[添加] 添加远程仓库..." -ForegroundColor Yellow
    git remote add origin $GitHubRepo
}

# 尝试推送
Write-Host ""
Write-Host "[4/5] 尝试推送到GitHub..." -ForegroundColor Yellow
Write-Host "[提示] 如果需要认证，会弹出登录窗口" -ForegroundColor Yellow

$pushAttempts = 0
$maxAttempts = 3
$pushed = $false

while ($pushAttempts -lt $maxAttempts -and -not $pushed) {
    $pushAttempts++
    Write-Host ""
    Write-Host "尝试 #$pushAttempts..." -ForegroundColor Cyan
    
    # 尝试推送
    $result = git push -u origin main 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[成功] 推送成功！" -ForegroundColor Green
        $pushed = $true
    } else {
        Write-Host "[失败] 推送失败" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        
        if ($pushAttempts -lt $maxAttempts) {
            Write-Host ""
            Write-Host "等待5秒后重试..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            # 尝试使用GitHub CLI
            Write-Host "检查是否安装了GitHub CLI..." -ForegroundColor Yellow
            $gh = Get-Command gh -ErrorAction SilentlyContinue
            if ($gh) {
                Write-Host "[尝试] 使用GitHub CLI认证..." -ForegroundColor Yellow
                gh auth status
            }
        }
    }
}

Write-Host ""
Write-Host "[5/5] 推送结果:" -ForegroundColor Yellow

if ($pushed) {
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host "✅ 推送成功！" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host ""
    Write-Host "GitHub仓库: https://github.com/diskk-create/wangzhe-autoclicker" -ForegroundColor Cyan
    Write-Host "Actions页面: https://github.com/diskk-create/wangzhe-autoclicker/actions" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "下一步:" -ForegroundColor Yellow
    Write-Host "1. 访问Actions页面查看构建进度" -ForegroundColor White
    Write-Host "2. 等待约20分钟构建完成" -ForegroundColor White
    Write-Host "3. 下载生成的APK文件" -ForegroundColor White
} else {
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host "❌ 推送失败" -ForegroundColor Red
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "1. 网络连接问题" -ForegroundColor White
    Write-Host "2. 需要GitHub认证" -ForegroundColor White
    Write-Host "3. 仓库权限问题" -ForegroundColor White
    Write-Host ""
    Write-Host "解决方案:" -ForegroundColor Yellow
    Write-Host "1. 使用GitHub Desktop:" -ForegroundColor White
    Write-Host "   - 打开GitHub Desktop" -ForegroundColor Gray
    Write-Host "   - File > Add local repository" -ForegroundColor Gray
    Write-Host "   - 选择: $ProjectDir" -ForegroundColor Gray
    Write-Host "   - 点击 Publish repository" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. 使用GitHub CLI:" -ForegroundColor White
    Write-Host "   gh auth login" -ForegroundColor Gray
    Write-Host "   git push -u origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. 检查网络:" -ForegroundColor White
    Write-Host "   Test-NetConnection github.com -Port 443" -ForegroundColor Gray
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

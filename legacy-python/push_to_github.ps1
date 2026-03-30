#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git推送脚本
自动初始化Git并推送到GitHub
"""

import os
import subprocess
import sys

# 项目目录
PROJECT_DIR = r'C:\Users\Administrator\.openclaw\workspace\wangzhe_autoclicker_v3'
GITHUB_REPO = 'https://github.com/diskk-create/wangzhe-autoclicker.git'

def run_command(cmd, cwd=None):
    """运行命令"""
    print(f'执行: {cmd}')
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd or PROJECT_DIR,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode == 0

def main():
    """主函数"""
    print('=' * 70)
    print('王者荣耀自动点击器 v3.0 - Git推送脚本')
    print('=' * 70)
    print()

    # 检查目录
    if not os.path.exists(PROJECT_DIR):
        print(f'错误: 项目目录不存在: {PROJECT_DIR}')
        return False

    os.chdir(PROJECT_DIR)
    print(f'工作目录: {PROJECT_DIR}')
    print()

    # 1. 初始化Git
    print('[1/6] 初始化Git仓库...')
    if not run_command('git init'):
        print('警告: Git已初始化或初始化失败')
    print()

    # 2. 添加所有文件
    print('[2/6] 添加文件到暂存区...')
    if not run_command('git add .'):
        print('错误: 添加文件失败')
        return False
    print()

    # 3. 提交
    print('[3/6] 提交更改...')
    commit_msg = 'v3.0: 完整重构版本\n\n修复:\n- 启动崩溃问题\n- 横屏闪退问题\n- 分辨率不适配问题\n- 模拟器不支持问题\n\n新增:\n- 分辨率自动适配\n- 设备检测和兼容性检查\n- 悬浮窗生命周期管理\n- 多架构支持（ARM + x86）'
    if not run_command(f'git commit -m "{commit_msg}"'):
        print('警告: 没有更改需要提交或提交失败')
    print()

    # 4. 设置分支
    print('[4/6] 设置主分支...')
    run_command('git branch -M main')
    print()

    # 5. 添加远程仓库
    print('[5/6] 添加远程仓库...')
    run_command('git remote remove origin')  # 先删除旧的
    if not run_command(f'git remote add origin {GITHUB_REPO}'):
        print('错误: 添加远程仓库失败')
        return False
    print()

    # 6. 推送
    print('[6/6] 推送到GitHub...')
    print('这可能需要输入GitHub用户名和密码...')
    if not run_command('git push -u origin main --force'):
        print('错误: 推送失败')
        print('请确保:')
        print('  1. GitHub仓库已创建')
        print('  2. 有推送权限')
        print('  3. 网络连接正常')
        return False
    print()

    print('=' * 70)
    print('✅ 推送成功！')
    print('=' * 70)
    print()
    print(f'GitHub仓库: {GITHUB_REPO}')
    print(f'Actions页面: {GITHUB_REPO.replace(".git", "/actions")}')
    print()
    print('下一步:')
    print('1. 访问GitHub仓库页面')
    print('2. 点击 Actions 标签')
    print('3. 等待自动构建（约20分钟）')
    print('4. 构建完成后下载APK')
    print()

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

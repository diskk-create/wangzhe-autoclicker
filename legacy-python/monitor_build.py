#!/usr/bin/env python3
"""
持续监控GitHub Actions构建状态
每2分钟检查一次，直到构建完成
"""
import requests
import time
import sys

REPO_OWNER = "diskk-create"
REPO_NAME = "wangzhe-autoclicker"
CHECK_INTERVAL = 120  # 2分钟

def check_build_status():
    """检查最新的构建状态"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data['workflow_runs']:
            print("没有找到workflow运行")
            return None

        run = data['workflow_runs'][0]  # 最新的运行
        status = run['status']
        conclusion = run.get('conclusion', 'running')
        html_url = run['html_url']

        return {
            'status': status,
            'conclusion': conclusion,
            'url': html_url,
            'name': run['name'],
            'created_at': run['created_at']
        }

    except Exception as e:
        print(f"获取状态失败: {e}")
        return None

def monitor():
    """持续监控"""
    print("=" * 70)
    print("GitHub Actions 构建监控")
    print("=" * 70)
    print()

    check_count = 0

    while True:
        check_count += 1
        print(f"[检查 #{check_count}] {time.strftime('%H:%M:%S')}")

        result = check_build_status()

        if result:
            status = result['status']
            conclusion = result['conclusion']

            # 状态图标
            if status == 'completed':
                if conclusion == 'success':
                    icon = '[OK]'
                    print(f"{icon} 构建成功！")
                elif conclusion == 'failure':
                    icon = '[FAIL]'
                    print(f"{icon} 构建失败！")
                else:
                    icon = f'[{conclusion}]'
                    print(f"{icon} 构建结束: {conclusion}")

                print()
                print(f"详情: {result['url']}")
                print()
                break
            elif status == 'in_progress':
                print(f"[RUNNING] 构建进行中...")
            elif status == 'queued':
                print(f"[QUEUED] 等待构建...")
            else:
                print(f"[{status}] 状态: {status}")

            print(f"链接: {result['url']}")
        else:
            print("无法获取状态")

        print()
        print(f"等待 {CHECK_INTERVAL} 秒后再次检查...")
        print("-" * 70)
        print()
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    try:
        monitor()
    except KeyboardInterrupt:
        print()
        print("监控已停止")
        sys.exit(0)

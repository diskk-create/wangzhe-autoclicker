#!/usr/bin/env python3
"""
获取所有构建记录，找到成功的版本
"""
import requests
import json

REPO_OWNER = "diskk-create"
REPO_NAME = "wangzhe-autoclicker"

def get_all_runs():
    """获取所有构建记录"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        print("=" * 70)
        print("所有构建记录")
        print("=" * 70)
        print()

        for i, run in enumerate(data['workflow_runs'][:10], 1):
            status = run['status']
            conclusion = run.get('conclusion', 'running')
            created_at = run['created_at']
            head_sha = run['head_sha'][:7]
            html_url = run['html_url']

            # 状态图标
            if conclusion == 'success':
                icon = '[SUCCESS]'
            elif conclusion == 'failure':
                icon = '[FAIL]'
            elif conclusion == 'cancelled':
                icon = '[CANCEL]'
            else:
                icon = '[RUNNING]'

            print(f"{i}. {icon} {run['name']}")
            print(f"   提交: {head_sha}")
            print(f"   状态: {status} | 结果: {conclusion}")
            print(f"   时间: {created_at}")
            print(f"   链接: {html_url}")
            print()

            # 如果是成功的构建，显示详细信息
            if conclusion == 'success':
                print(f"   ★ 找到成功构建！")
                print()

        return data['workflow_runs']

    except Exception as e:
        print(f"获取构建记录失败: {e}")
        return None

if __name__ == '__main__':
    get_all_runs()

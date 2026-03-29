#!/usr/bin/env python3
"""
获取GitHub Actions构建日志
"""
import requests
import json
import sys

# GitHub仓库信息
REPO_OWNER = "diskk-create"
REPO_NAME = "wangzhe-autoclicker"

def get_workflow_runs():
    """获取最近的workflow运行"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("=" * 70)
        print("GitHub Actions 构建状态")
        print("=" * 70)
        print()
        
        for i, run in enumerate(data['workflow_runs'][:5], 1):
            status = run['status']
            conclusion = run.get('conclusion', 'running')
            created_at = run['created_at']
            html_url = run['html_url']
            
            # 状态图标
            if conclusion == 'success':
                icon = '[OK]'
            elif conclusion == 'failure':
                icon = '[FAIL]'
            elif conclusion == 'cancelled':
                icon = '[STOP]'
            else:
                icon = '[RUNNING]'
            
            print(f"{i}. {icon} {run['name']}")
            print(f"   状态: {status} | 结果: {conclusion}")
            print(f"   时间: {created_at}")
            print(f"   链接: {html_url}")
            print()
            
            # 如果失败，获取详细日志
            if conclusion == 'failure':
                print(f"   正在获取失败详情...")
                get_failure_logs(run['id'], run['jobs_url'])
                break
        
        return data['workflow_runs']
        
    except Exception as e:
        print(f"获取workflow失败: {e}")
        return None

def get_failure_logs(run_id, jobs_url):
    """获取失败的详细日志"""
    try:
        # 获取jobs
        response = requests.get(jobs_url, timeout=10)
        response.raise_for_status()
        jobs_data = response.json()
        
        print()
        print("   " + "=" * 66)
        print("   失败的Job详情:")
        print("   " + "=" * 66)
        
        for job in jobs_data['jobs']:
            if job['conclusion'] == 'failure':
                print(f"   Job: {job['name']}")
                print(f"   状态: {job['status']} | 结果: {job['conclusion']}")
                print()
                
                # 获取失败步骤
                for step in job['steps']:
                    if step['conclusion'] == 'failure':
                        print(f"   [FAIL] 失败步骤: {step['name']}")
                        print(f"      开始: {step['started_at']}")
                        print(f"      结束: {step['completed_at']}")
                        print()
                
                # 获取日志URL
                log_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/jobs/{job['id']}/logs"
                print(f"   日志URL: {log_url}")
                print()
                print("   请访问上述URL查看详细日志，或手动查看:")
                print(f"   {job['html_url']}")
                print()
                
    except Exception as e:
        print(f"   获取详细日志失败: {e}")

if __name__ == '__main__':
    print("正在获取GitHub Actions构建状态...")
    print()
    get_workflow_runs()

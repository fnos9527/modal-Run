import os
import json
import time
import subprocess
import platform
import random
import threading
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
import modal

# ========== Modal 配置 ==========
# 从环境变量读取部署区域，由工作流注入
DEPLOY_REGION = os.environ.get('DEPLOY_REGION', 'us-east')

# ========== Modal 镜像定义 ==========
image = modal.Image.debian_slim().pip_install(
    "fastapi==0.115.12",
    "pydantic==2.11.7",
    "requests",
    "psutil",
    "uvicorn",
)

app = modal.App("komari-app", image=image)

# ========== FastAPI 实例 ==========
web_app = FastAPI(
    title="Cloud Services Platform",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# ========== 全局启动控制 ==========
_agent_started = False
_agent_lock = threading.Lock()
_project_url = None

# ========== 伪装页面 HTML ==========
FAKE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle Cloud Infrastructure</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f9; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; }
        .status-badge { color: #059669; background: #ecfdf5; padding: 8px 16px; border-radius: 20px; font-size: 14px; display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Cloud Services Node</h1>
        <p>Enterprise-grade infrastructure powering global applications.</p>
        <div class="status-badge">● System Operational</div>
    </div>
</body>
</html>"""

# ========== 辅助函数 ==========

def write_log(message):
    try:
        with open('/tmp/agent.log', 'a') as f:
            f.write(f"[{time.ctime()}] {message}\n")
    except Exception:
        pass

def get_system_architecture():
    architecture = platform.machine().lower()
    if 'arm' in architecture or 'aarch64' in architecture:
        return 'arm64'
    return 'amd64'

def run_komari_agent():
    """启动 Komari Agent 的核心逻辑"""
    server = os.environ.get('KOMARI_SERVER', '')
    key = os.environ.get('KOMARI_KEY', '')
    
    if not server or not key:
        write_log("Error: KOMARI_SERVER or KOMARI_KEY is missing.")
        return

    arch = get_system_architecture()
    # 伪装文件名
    disguise_name = "sys_worker"
    file_path = "/tmp"
    agent_full_path = os.path.join(file_path, disguise_name)
    
    # Komari 官方下载地址
    download_url = f"https://github.com/komari-monitor/komari/releases/latest/download/komari-linux-{arch}"

    try:
        import requests
        write_log(f"Downloading Komari for {arch}...")
        response = requests.get(download_url, timeout=60)
        response.raise_for_status()
        with open(agent_full_path, 'wb') as f:
            f.write(response.content)
        
        # 赋予执行权限
        os.chmod(agent_full_path, 0o755)
        
        # 启动命令 (Komari 参数通常为 -s 地址 -k 密钥)
        # 如果

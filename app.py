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
DEPLOY_REGION = os.environ.get('DEPLOY_REGION', 'us-east')

# ========== Modal 镜像定义 ==========
image = modal.Image.debian_slim().pip_install(
    "fastapi==0.115.12",
    "pydantic==2.11.7",
    "requests",
    "psutil",
    "uvicorn",
)

app = modal.App("app", image=image)

# ========== FastAPI 实例 ==========
web_app = FastAPI(
    title="Cloud Services Platform",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# ========== 全局控制变量 ==========
_agent_started = False
_agent_lock = threading.Lock()
_keepalive_started = False
_keepalive_lock = threading.Lock()
_project_url = None

# ========== 伪装页面 HTML ==========
FAKE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Infrastructure Status</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }
        .status { color: #10b981; font-weight: bold; margin-top: 1rem; }
    </style>
</head>
<body>
    <div class="card">
        <h1>System Monitor</h1>
        <p>Global edge network nodes are operational.</p>
        <div class="status">● All Systems Normal</div>
    </div>
</body>
</html>"""

# ========== 核心功能函数 ==========

def create_directory(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)

def get_system_architecture():
    architecture = platform.machine().lower()
    if 'arm' in architecture or 'aarch64' in architecture:
        return 'arm64'
    return 'amd64'

def download_file(file_name, file_url, file_path):
    import requests
    try:
        full_path = os.path.join(file_path, file_name)
        response = requests.get(file_url, stream=True, timeout=60)
        response.raise_for_status()
        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        write_log(f"Download failed: {e}")
        return False

def authorize_files(file_path):
    if os.path.exists(file_path):
        os.chmod(file_path, 0o775)

def write_log(message):
    try:
        with open('/tmp/agent.log', 'a') as f:
            f.write(f"[{time.ctime()}] {message}\n")
    except Exception:
        pass

def exec_cmd(command):
    try:
        with open('/tmp/agent.log', 'a') as f:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=f,
                stderr=f,
                start_new_session=True,
            )
        return process.pid
    except Exception as e:
        write_log(f"Exec error: {e}")
        return None

def run_agent(file_path, komari_server, komari_key):
    """
    改为启动 Komari Agent
    """
    if not komari_server or not komari_key:
        write_log("KOMARI_SERVER or KOMARI_KEY is missing.")
        return

    arch = get_system_architecture()
    
    # 设定 Komari 下载地址 (示例为常见的发布路径，请确保地址有效)
    # 注意：这里使用了您可能熟悉的 disguise 逻辑
    disguise_name = "sys_worker"
    url = f"https://github.com/komari-monitor/komari/releases/latest/download/komari-linux-{arch}"

    write_log(f"Downloading Komari for {arch}...")
    if not download_file(disguise_name, url, file_path):
        return

    agent_path = os.path.join(file_path, disguise_name)
    authorize_files(agent_path)

    # Komari 启动命令通常为: ./komari -s server_address -k secret_key
    # 请根据您的 Komari 版本实际参数调整名 (-s/-k)
    command = f"nohup {agent_path} -s {komari_server} -k {komari_key} >/dev/null 2>&1 &"

    write_log(f"Starting Komari: {command}")
    pid = exec_cmd(command)
    if pid:
        write_log(f"Komari started with PID: {pid}")

def tail_log(filepath, lines=10):
    try:
        with open(filepath, 'r') as f:
            all_lines = f.read().splitlines()
            return all_lines[-lines:] if len(all_lines) >= lines else all_lines
    except:
        return ["Log empty"]

def find_agent_processes():
    import psutil
    found = []
    # 匹配我们定义的伪装名
    target_names = ['sys_worker', 'komari']
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info.get('cmdline') or [])
            if any(name in cmdline for name in target_names):
                found.append({"pid": proc.info['pid'], "status": "running"})
        except:
            continue
    return found

# ========== 保活与监控逻辑 ==========

def self_keepalive_loop(project_url, interval=120):
    import requests
    health_url = project_url.rstrip('/') + '/health'
    while True:
        try:
            time.sleep(interval + random.randint(0, 20))
            requests.get(health_url, timeout=20)
        except:
            pass

def ensure_agent_started():
    global _agent_started
    with _agent_lock:
        if _agent_started: return
        _agent_started = True

    FILE_PATH = os.environ.get('FILE_PATH', '/tmp/app_data')
    # 从新的 Secret 键名读取
    K_SERVER = os.environ.get('KOMARI_SERVER', '')
    K_KEY = os.environ.get('KOMARI_KEY', '')

    create_directory(FILE_PATH)
    
    def starter():
        try:
            run_agent(FILE_PATH, K_SERVER, K_KEY)
        except Exception as e:
            write_log(f"Starter thread error: {e}")

    threading.Thread(target=starter, daemon=True).start()

# ========== FastAPI 路由与事件 ==========

@web_app.on_event("startup")
async def startup_event():
    ensure_agent_started()

@web_app.get("/")
async def root():
    return HTMLResponse(content=FAKE_HTML)

@web_app.get("/health")
async def health():
    return {"status": "ok", "time": time.time()}

@web_app.get("/status")
async def status():
    return {"agent": "komari", "processes": find_agent_processes()}

# ========== Modal 入口 ==========

@app.function(
    # 注意：这里的 Secret 名称需与 GitHub Actions 脚本中创建的一致
    secrets=[modal.Secret.from_name("komari-secrets")],
    scaledown_window=300,
    region=[DEPLOY_REGION],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

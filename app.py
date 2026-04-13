import os
import json
import time
import subprocess
import platform
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import modal

# ========== Modal 配置 ==========
DEPLOY_REGION = os.environ.get('DEPLOY_REGION', 'us-east')

# ========== Modal 镜像定义 ==========
image = modal.Image.debian_slim().pip_install(
    "fastapi==0.115.12",
    "requests",
    "psutil",
    "uvicorn",
)

app = modal.App("komari-app", image=image)
web_app = FastAPI()

# ========== 状态控制 ==========
_agent_started = False
_agent_lock = threading.Lock()

# ========== 伪装页面 HTML ==========
FAKE_HTML = """<!DOCTYPE html>
<html>
<head><title>System Status</title></head>
<body><h1 style='text-align:center;margin-top:20%'>Node Operational</h1></body>
</html>"""

# ========== 核心功能 ==========

def write_log(message):
    try:
        with open('/tmp/agent.log', 'a') as f:
            f.write(f"[{time.ctime()}] {message}\n")
    except:
        pass

def get_arch():
    m = platform.machine().lower()
    return 'arm64' if 'arm' in m or 'aarch64' in m else 'amd64'

def run_komari_agent():
    """下载并启动 Komari Agent"""
    server = os.environ.get('KOMARI_SERVER', '')
    key = os.environ.get('KOMARI_KEY', '')
    
    if not server or not key:
        write_log("Missing SERVER or KEY")
        return

    arch = get_arch()
    path = "/tmp/sys_worker"
    url = f"https://github.com/komari-monitor/komari/releases/latest/download/komari-linux-{arch}"

    try:
        import requests
        write_log(f"Downloading Komari for {arch}...")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(path, 'wb') as f:
            f.write(r.content)
        
        os.chmod(path, 0o755)
        # 启动命令
        cmd = f"nohup {path} -s {server} -k {key} >/dev/null 2>&1 &"
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        write_log("Komari Agent started.")
    except Exception as e:
        write_log(f"Error: {str(e)}")

def ensure_agent_started():
    global _agent_started
    with _agent_lock:
        if _agent_started:
            return
        _agent_started = True
    threading.Thread(target=run_komari_agent, daemon=True).start()

# ========== 路由 ==========

@web_app.on_event("startup")
async def startup_event():
    ensure_agent_started()

@web_app.get("/")
async def root():
    return HTMLResponse(content=FAKE_HTML)

@web_app.get("/health")
async def health():
    return {"status": "ok"}

# ========== Modal 入口 ==========

@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[DEPLOY_REGION],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

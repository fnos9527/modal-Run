import os
import time
import subprocess
import platform
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import modal

# ========== Modal 配置 ==========
DEPLOY_REGION = os.environ.get('DEPLOY_REGION', 'us-east')

image = modal.Image.debian_slim().pip_install(
    "fastapi==0.115.12",
    "requests",
    "psutil",
)

app = modal.App("komari-app", image=image)
web_app = FastAPI()

_agent_started = False
_agent_lock = threading.Lock()

# ========== 辅助功能 ==========

def write_log(message):
    try:
        with open('/tmp/agent.log', 'a') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except:
        pass

def run_komari_agent():
    server = os.environ.get('KOMARI_SERVER', '')
    key = os.environ.get('KOMARI_KEY', '')
    
    # 记录环境变量状态（不打印具体的Key，保护安全）
    if not server:
        write_log("Error: KOMARI_SERVER environment variable is empty!")
    if not key:
        write_log("Error: KOMARI_KEY environment variable is empty!")
    
    if not server or not key:
        return

    arch = platform.machine().lower()
    arch_suffix = 'arm64' if 'arm' in arch or 'aarch64' in arch else 'amd64'
    
    path = "/tmp/sys_worker"
    url = f"https://github.com/komari-monitor/komari/releases/latest/download/komari-linux-{arch_suffix}"

    try:
        import requests
        write_log(f"Downloading Agent from: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(path, 'wb') as f:
            f.write(r.content)
        
        os.chmod(path, 0o755)
        # 启动命令：确保使用 -s 和 -k 参数
        cmd = f"nohup {path} -s {server} -k {key} > /tmp/komari_exec.log 2>&1 &"
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        write_log("Agent process launched.")
    except Exception as e:
        write_log(f"Critical Error: {str(e)}")

def ensure_agent_started():
    global _agent_started
    with _agent_lock:
        if _agent_started:
            return
        _agent_started = True
    threading.Thread(target=run_komari_agent, daemon=True).start()

# ========== 路由接口 ==========

@web_app.on_event("startup")
async def startup_event():
    ensure_agent_started()

@web_app.get("/")
async def root():
    return HTMLResponse("<h1>Node Status: Online</h1>")

# 这个接口现在修好了！
@web_app.get("/logs")
async def get_logs():
    if os.path.exists('/tmp/agent.log'):
        with open('/tmp/agent.log', 'r') as f:
            return JSONResponse({"logs": f.readlines()})
    return JSONResponse({"logs": ["Log file not created yet."]})

# ========== Modal 运行入口 ==========

@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[DEPLOY_REGION],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

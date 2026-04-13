import os
import time
import subprocess
import platform
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import modal

# 1. 镜像配置
image = modal.Image.debian_slim().pip_install("fastapi", "requests")

# 2. 创建 App
app = modal.App("komari-app", image=image)
web_app = FastAPI()

def write_log(msg):
    with open('/tmp/agent.log', 'a') as f:
        f.write(f"[{time.ctime()}] {msg}\n")

def run_agent():
    # 自动处理地址：Cloudflare 隧道必须走 HTTPS (443)
    raw_server = os.environ.get('KOMARI_SERVER', '')
    server_host = raw_server.replace('https://', '').replace('http://', '').split(':')[0]
    
    # 强制指定 443 端口，因为 Cloudflare 隧道基于 HTTPS
    server = f"{server_host}:443"
    key = os.environ.get('KOMARI_KEY', '')
    
    if not server_host or not key:
        write_log("Error: SERVER or KEY is empty!")
        return

    # 清理旧进程
    subprocess.run("pkill -9 agent", shell=True)

    arch = 'arm64' if 'arm' in platform.machine().lower() else 'amd64'
    url = f"https://github.com/komari-monitor/komari/releases/latest/download/komari-linux-{arch}"
    
    try:
        import requests
        write_log(f"Downloading agent...")
        r = requests.get(url, timeout=15)
        with open("/tmp/agent", "wb") as f:
            f.write(r.content)
        os.chmod("/tmp/agent", 0o755)
        
        # --- 核心修正：使用正确的新版命令参数 ---
        # 1. 使用 'agent' 子命令
        # 2. 使用 --server 和 --key 全称
        # 3. 增加 --tls (Cloudflare 必须加密)
        write_log(f"Connecting to {server} via Cloudflare Tunnel...")
        with open('/tmp/exec.log', 'w') as log_file:
            subprocess.Popen(
                ["/tmp/agent", "agent", "--server", server, "--key", key, "--tls"],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid
            )
        write_log("Agent launched with correct command. Checking connection...")
    except Exception as e:
        write_log(f"Failed: {str(e)}")

@web_app.on_event("startup")
async def startup():
    threading.Thread(target=run_agent, daemon=True).start()

@web_app.get("/")
async def index():
    return HTMLResponse("<h1>System Status: Running</h1>")

@web_app.get("/logs")
async def logs():
    data = {"setup": [], "agent_output": []}
    if os.path.exists('/tmp/agent.log'):
        with open('/tmp/agent.log', 'r') as f:
            data["setup"] = f.readlines()
    if os.path.exists('/tmp/exec.log'):
        with open('/tmp/exec.log', 'r') as f:
            data["agent_output"] = f.readlines()
    return data

# 3. Modal 部署入口
@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[os.environ.get('DEPLOY_REGION', 'us-east')],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

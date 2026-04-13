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
    # 处理地址：Cloudflare 隧道必须走 HTTPS (443)
    raw_server = os.environ.get('KOMARI_SERVER', '')
    server_host = raw_server.replace('https://', '').replace('http://', '').split(':')[0]
    
    # 强制指定 443 端口，确保穿透 Cloudflare
    server = f"{server_host}:443"
    key = os.environ.get('KOMARI_KEY', '')
    
    if not server_host or not key:
        write_log("Error: SERVER or KEY is empty!")
        return

    # 清理旧进程
    subprocess.run("pkill -9 komari-agent", shell=True)

    # 3. 根据架构选择下载地址（使用你提供的最新 Agent 链接）
    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch64' in arch:
        url = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.93/komari-agent-linux-arm64"
    else:
        url = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.93/komari-agent-linux-amd64"
    
    path = "/tmp/komari-agent"
    
    try:
        import requests
        write_log(f"Downloading REAL Agent from: {url}")
        r = requests.get(url, timeout=15)
        with open(path, "wb") as f:
            f.write(r.content)
        os.chmod(path, 0o755)
        
        # --- 核心修正：使用专用 Agent 的启动命令 ---
        # 专用客户端通常使用 -s 和 -k，且 Cloudflare 必须带 --tls
        write_log(f"Connecting to {server} via Cloudflare...")
        with open('/tmp/exec.log', 'w') as log_file:
            subprocess.Popen(
                [path, "-s", server, "-k", key, "--tls"],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid
            )
        write_log("Real Agent launched successfully!")
    except Exception as e:
        write_log(f"Failed: {str(e)}")

@web_app.on_event("startup")
async def startup():
    threading.Thread(target=run_agent, daemon=True).start()

@web_app.get("/")
async def index():
    return HTMLResponse("<h1>Komari Agent: Running</h1>")

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

# 4. Modal 部署
@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[os.environ.get('DEPLOY_REGION', 'us-east')],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

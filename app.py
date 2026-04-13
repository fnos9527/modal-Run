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
    # 自动处理服务端地址：去掉 https:// 并确保使用 443 端口
    raw_server = os.environ.get('KOMARI_SERVER', '')
    server = raw_server.replace('https://', '').replace('http://', '')
    
    # 如果用户没填端口，默认补上 :443
    if ':' not in server:
        server = f"{server}:443"
    
    key = os.environ.get('KOMARI_KEY', '')
    
    if not server or not key:
        write_log("Error: SERVER or KEY is empty!")
        return

    # 清理可能存在的旧进程
    subprocess.run("pkill -9 agent", shell=True)

    arch = 'arm64' if 'arm' in platform.machine().lower() else 'amd64'
    url = f"https://github.com/komari-monitor/komari/releases/latest/download/komari-linux-{arch}"
    
    try:
        import requests
        write_log(f"Downloading agent for {arch}...")
        r = requests.get(url, timeout=15)
        with open("/tmp/agent", "wb") as f:
            f.write(r.content)
        os.chmod("/tmp/agent", 0o755)
        
        # 启动 Agent
        # -s 指定服务器, -k 指定密钥, --tls 开启加密 (因为你是 https 域名)
        write_log(f"Connecting to {server} with TLS...")
        with open('/tmp/exec.log', 'w') as log_file:
            subprocess.Popen(
                ["/tmp/agent", "-s", server, "-k", key, "--tls"],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid
            )
        write_log("Agent process launched with --tls.")
    except Exception as e:
        write_log(f"Failed: {str(e)}")

@web_app.on_event("startup")
async def startup():
    # 容器启动时异步开启 Agent
    threading.Thread(target=run_agent, daemon=True).start()

@web_app.get("/")
async def index():
    return HTMLResponse("<h1>System Operational</h1>")

@web_app.get("/logs")
async def logs():
    data = {"setup_status": [], "connection_error": []}
    if os.path.exists('/tmp/agent.log'):
        with open('/tmp/agent.log', 'r') as f:
            data["setup_status"] = f.readlines()
    if os.path.exists('/tmp/exec.log'):
        with open('/tmp/exec.log', 'r') as f:
            data["connection_error"] = f.readlines()
    return data

# 3. Modal 部署入口
@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[os.environ.get('DEPLOY_REGION', 'us-east')],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

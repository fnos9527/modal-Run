import os
import time
import subprocess
import platform
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import modal

# 1. 定义镜像
image = modal.Image.debian_slim().pip_install("fastapi", "requests")

# 2. 创建 App
app = modal.App("komari-app", image=image)
web_app = FastAPI()

# 写入日志的函数
def write_log(msg):
    with open('/tmp/agent.log', 'a') as f:
        f.write(f"[{time.ctime()}] {msg}\n")

# 启动 Agent 的函数
def run_agent():
    # 从环境变量读取（这些变量必须由 Secret 提供）
    server = os.environ.get('KOMARI_SERVER', '')
    key = os.environ.get('KOMARI_KEY', '')
    
    if not server or not key:
        write_log(f"Error: Server({server}) or Key is empty!")
        return

    arch = 'arm64' if 'arm' in platform.machine().lower() else 'amd64'
    url = f"https://github.com/komari-monitor/komari/releases/latest/download/komari-linux-{arch}"
    
    try:
        import requests
        write_log("Downloading agent...")
        r = requests.get(url)
        with open("/tmp/agent", "wb") as f:
            f.write(r.content)
        os.chmod("/tmp/agent", 0o755)
        
        # 启动
        subprocess.Popen(f"nohup /tmp/agent -s {server} -k {key} >/dev/null 2>&1 &", shell=True)
        write_log("Agent started successfully!")
    except Exception as e:
        write_log(f"Failed: {str(e)}")

@web_app.on_event("startup")
async def startup():
    threading.Thread(target=run_agent, daemon=True).start()

@web_app.get("/")
async def index():
    return HTMLResponse("<h1>Running</h1>")

@web_app.get("/logs")
async def logs():
    if os.path.exists('/tmp/agent.log'):
        return {"logs": open('/tmp/agent.log').readlines()}
    return {"msg": "No logs yet"}

# 3. 核心部署入口：必须指定 secrets 名字！！！
@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[os.environ.get('DEPLOY_REGION', 'us-east')],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

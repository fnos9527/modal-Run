import os
import time
import subprocess
import platform
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import modal

image = modal.Image.debian_slim().pip_install("fastapi", "requests")
app = modal.App("komari-app", image=image)
web_app = FastAPI()

def write_log(msg):
    with open('/tmp/agent.log', 'a') as f:
        f.write(f"[{time.ctime()}] {msg}\n")

def run_agent():
    server = os.environ.get('KOMARI_SERVER', '')
    key = os.environ.get('KOMARI_KEY', '')
    
    if not server or not key:
        write_log("Error: Variables missing!")
        return

    # 清除残留进程
    subprocess.run("pkill -9 agent", shell=True)

    arch = 'arm64' if 'arm' in platform.machine().lower() else 'amd64'
    url = f"https://github.com/komari-monitor/komari/releases/latest/download/komari-linux-{arch}"
    
    try:
        import requests
        write_log(f"Downloading agent to {arch}...")
        r = requests.get(url, timeout=10)
        with open("/tmp/agent", "wb") as f:
            f.write(r.content)
        os.chmod("/tmp/agent", 0o755)
        
        # --- 核心改进：把所有输出重定向到 /tmp/exec.log ---
        write_log(f"Starting agent connecting to {server}...")
        with open('/tmp/exec.log', 'w') as log_file:
            subprocess.Popen(
                ["/tmp/agent", "-s", server, "-k", key],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid
            )
        write_log("Process launched. Check /logs for connection status.")
    except Exception as e:
        write_log(f"Failed: {str(e)}")

@web_app.on_event("startup")
async def startup():
    threading.Thread(target=run_agent, daemon=True).start()

@web_app.get("/")
async def index():
    return HTMLResponse("<h1>Node Online</h1>")

# 这个接口会展示具体的连接报错
@web_app.get("/logs")
async def logs():
    data = {"setup": [], "connection_error": []}
    if os.path.exists('/tmp/agent.log'):
        with open('/tmp/agent.log', 'r') as f:
            data["setup"] = f.readlines()
    if os.path.exists('/tmp/exec.log'):
        with open('/tmp/exec.log', 'r') as f:
            data["connection_error"] = f.readlines()
    return data

@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[os.environ.get('DEPLOY_REGION', 'us-east')],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

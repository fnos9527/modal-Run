import os
import time
import subprocess
import platform
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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
    # 获取变量并自动补全协议
    raw_server = os.environ.get('KOMARI_SERVER', '')
    if not raw_server.startswith('http'):
        endpoint = f"https://{raw_server}"
    else:
        endpoint = raw_server
        
    token = os.environ.get('KOMARI_KEY', '')
    
    if not endpoint or not token:
        write_log("Error: SERVER or TOKEN is missing!")
        return

    # 清理可能残留的进程
    subprocess.run("pkill -9 komari-agent", shell=True)

    # 3. 下载官方指定的最新版 Agent
    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch64' in arch:
        url = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.93/komari-agent-linux-arm64"
    else:
        url = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.93/komari-agent-linux-amd64"
    
    path = "/tmp/komari-agent"
    
    try:
        import requests
        write_log(f"Downloading Agent from GitHub...")
        r = requests.get(url, timeout=15)
        with open(path, "wb") as f:
            f.write(r.content)
        os.chmod(path, 0o755)
        
        # --- 核心启动逻辑 (完全对应官方参数) ---
        write_log(f"Starting Agent with endpoint: {endpoint}")
        with open('/tmp/exec.log', 'w') as log_file:
            # 模仿官方脚本的启动方式
            subprocess.Popen(
                [path, "-e", endpoint, "-t", token],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid
            )
        write_log("Agent is now running in background.")
    except Exception as e:
        write_log(f"Critical Failure: {str(e)}")

@web_app.on_event("startup")
async def startup():
    threading.Thread(target=run_agent, daemon=True).start()

@web_app.get("/")
async def index():
    return HTMLResponse("<h1>Komari Agent Status: Online</h1>")

@web_app.get("/logs")
async def logs():
    data = {"setup": [], "agent_runtime_logs": []}
    if os.path.exists('/tmp/agent.log'):
        with open('/tmp/agent.log', 'r') as f:
            data["setup"] = f.readlines()
    if os.path.exists('/tmp/exec.log'):
        with open('/tmp/exec.log', 'r') as f:
            data["agent_runtime_logs"] = f.readlines()
    return data

# 4. Modal 部署入口
@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[os.environ.get('DEPLOY_REGION', 'us-east')],
)
@modal.asgi_app()
def fastapi_app():
    return web_app

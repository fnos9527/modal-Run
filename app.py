import os
import time
import subprocess
import platform
import threading
import signal
import requests
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

# --- 保活逻辑：每隔 120 秒访问一次自己 ---
def keep_alive(self_url):
    auto_access = os.environ.get('AUTO_ACCESS', 'true').lower() == 'true'
    interval = int(os.environ.get('KEEPALIVE_INTERVAL', 120))
    
    if not auto_access:
        return

    write_log(f"Keepalive task started. Interval: {interval}s")
    while True:
        try:
            # 访问自己的根目录
            requests.get(self_url, timeout=10)
            # write_log("Keepalive ping sent.") # 如果日志太多可以注释掉这行
        except:
            pass
        time.sleep(interval)

def run_agent():
    raw_server = os.environ.get('KOMARI_SERVER', '')
    if not raw_server.startswith('http'):
        endpoint = f"https://{raw_server}"
    else:
        endpoint = raw_server
        
    token = os.environ.get('KOMARI_KEY', '')
    
    if not endpoint or not token:
        write_log("Error: SERVER or TOKEN missing!")
        return

    # 清理旧进程 (原生 Python 方式)
    try:
        curr_pid = os.getpid()
        for pid in os.listdir('/proc'):
            if pid.isdigit() and int(pid) != curr_pid:
                try:
                    with open(f'/proc/{pid}/cmdline', 'r') as f:
                        if 'komari-agent' in f.read():
                            os.kill(int(pid), signal.SIGKILL)
                except: pass
    except: pass

    # 下载并启动 Agent
    arch = platform.machine().lower()
    suffix = "arm64" if 'arm' in arch or 'aarch64' in arch else "amd64"
    url = f"https://github.com/komari-monitor/komari-agent/releases/download/1.1.93/komari-agent-linux-{suffix}"
    path = "/tmp/komari-agent"
    
    try:
        if not os.path.exists(path):
            r = requests.get(url, timeout=15)
            with open(path, "wb") as f: f.write(r.content)
            os.chmod(path, 0o755)
        
        write_log(f"Starting Agent...")
        with open('/tmp/exec.log', 'a') as log_file:
            process = subprocess.Popen(
                [path, "-e", endpoint, "-t", token],
                stdout=log_file, stderr=log_file, preexec_fn=os.setsid
            )
            process.wait()
            time.sleep(10)
            run_agent() 
    except Exception as e:
        write_log(f"Error: {e}")
        time.sleep(10)
        run_agent()

@web_app.on_event("startup")
async def startup():
    # 1. 启动 Agent
    threading.Thread(target=run_agent, daemon=True).start()
    
    # 2. 启动保活任务 (获取当前 Modal 的 URL)
    # 这里的 URL 需要在部署后才能确定，或者手动在 Secret 填入
    # 如果不想填，代码会尝试在第一次访问时自动获取
    self_url = f"https://{os.environ.get('MODAL_PROJECT_NAME', 'fnosnas')}--komari-app-fastapi-app.modal.run"
    threading.Thread(target=keep_alive, args=(self_url,), daemon=True).start()

@web_app.get("/")
async def index():
    return HTMLResponse("<h1>Operational</h1>")

@web_app.get("/logs")
async def logs():
    data = {"setup": [], "agent_runtime": []}
    if os.path.exists('/tmp/agent.log'):
        with open('/tmp/agent.log', 'r') as f: data["setup"] = f.readlines()[-20:]
    if os.path.exists('/tmp/exec.log'):
        with open('/tmp/exec.log', 'r') as f: data["agent_runtime"] = f.readlines()[-50:]
    return data

@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[os.environ.get('DEPLOY_REGION', 'us-east')],
    container_idle_timeout=300,
)
@modal.asgi_app()
def fastapi_app():
    return web_app

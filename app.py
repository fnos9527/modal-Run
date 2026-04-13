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

# 1. 镜像配置：安装必要的库
image = modal.Image.debian_slim().pip_install("fastapi", "requests")

# 2. 创建 App
app = modal.App("komari-app", image=image)
web_app = FastAPI()

def write_log(msg):
    with open('/tmp/agent.log', 'a') as f:
        f.write(f"[{time.ctime()}] {msg}\n")

# --- 保活逻辑：每隔指定秒数访问一次自己，防止容器进入深度休眠 ---
def keep_alive(self_url):
    auto_access = os.environ.get('AUTO_ACCESS', 'true').lower() == 'true'
    interval = int(os.environ.get('KEEPALIVE_INTERVAL', 120))
    
    if not auto_access:
        return

    write_log(f"Keepalive task started. Target: {self_url} | Interval: {interval}s")
    while True:
        try:
            # 访问自己的根目录，维持容器激活状态
            requests.get(self_url, timeout=10)
        except:
            pass
        time.sleep(interval)

def run_agent():
    # 获取环境变量
    raw_server = os.environ.get('KOMARI_SERVER', '')
    if not raw_server:
        write_log("Error: KOMARI_SERVER is empty!")
        return
        
    # 自动处理地址格式
    if not raw_server.startswith('http'):
        endpoint = f"https://{raw_server}"
    else:
        endpoint = raw_server
        
    token = os.environ.get('KOMARI_KEY', '')
    if not token:
        write_log("Error: KOMARI_KEY is missing!")
        return

    # 彻底清理旧的二进制进程（改用原生 Python，不依赖 pkill）
    try:
        curr_pid = os.getpid()
        for pid in os.listdir('/proc'):
            if pid.isdigit() and int(pid) != curr_pid:
                try:
                    with open(f'/proc/{pid}/cmdline', 'r') as f:
                        if 'komari-agent' in f.read():
                            os.kill(int(pid), signal.SIGKILL)
                except:
                    pass
    except Exception as e:
        write_log(f"Clean-up info: {e}")

    # 下载并启动 Agent (根据系统架构选择版本)
    arch = platform.machine().lower()
    suffix = "arm64" if 'arm' in arch or 'aarch64' in arch else "amd64"
    url = f"https://github.com/komari-monitor/komari-agent/releases/download/1.1.93/komari-agent-linux-{suffix}"
    path = "/tmp/komari-agent"
    
    try:
        if not os.path.exists(path):
            write_log(f"Downloading Agent for {suffix}...")
            r = requests.get(url, timeout=15)
            with open(path, "wb") as f:
                f.write(r.content)
            os.chmod(path, 0o755)
        
        # 使用官方推荐参数启动：-e (endpoint), -t (token)
        write_log(f"Starting Agent connecting to: {endpoint}")
        with open('/tmp/exec.log', 'a') as log_file:
            process = subprocess.Popen(
                [path, "-e", endpoint, "-t", token],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid
            )
            write_log(f"Agent (PID: {process.pid}) is running.")
            
            # 守护进程：如果进程退出，等待 10 秒后重启
            process.wait()
            write_log("Agent process exited unexpectedly. Restarting in 10s...")
            time.sleep(10)
            run_agent() 
    except Exception as e:
        write_log(f"Agent execution error: {str(e)}")
        time.sleep(10)
        run_agent()

@web_app.on_event("startup")
async def startup():
    # 1. 启动 Komari Agent
    threading.Thread(target=run_agent, daemon=True).start()
    
    # 2. 启动保活任务
    # 请确保项目名 fnosnas 和 app 名 komari-app 与你 Modal 的 URL 一致
    self_url = f"https://{os.environ.get('MODAL_PROJECT_NAME', 'fnosnas')}--komari-app-fastapi-app.modal.run"
    threading.Thread(target=keep_alive, args=(self_url,), daemon=True).start()

@web_app.get("/")
async def index():
    return HTMLResponse("<h1>Komari Agent Deployment Active</h1><p>Visit /logs for details.</p>")

@web_app.get("/logs")
async def logs():
    data = {"setup_status": [], "agent_runtime_output": []}
    if os.path.exists('/tmp/agent.log'):
        with open('/tmp/agent.log', 'r') as f:
            data["setup_status"] = f.readlines()[-20:]
    if os.path.exists('/tmp/exec.log'):
        with open('/tmp/exec.log', 'r') as f:
            data["agent_runtime_output"] = f.readlines()[-50:]
    return data

# 3. Modal 部署入口
@app.function(
    secrets=[modal.Secret.from_name("komari-secrets")],
    region=[os.environ.get('DEPLOY_REGION', 'us-east')],
    # 修正关键点：将 container_idle_timeout 更名为 scaledown_window
    scaledown_window=300, 
)
@modal.asgi_app()
def fastapi_app():
    return web_app

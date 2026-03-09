### Secrets 配置说明

以下是工作流所需的 GitHub Secrets 配置项，请确保在仓库的 **Settings → Secrets and variables → Actions** 中正确设置。

| Secret 名称 | 是否必填 | 默认值 | 说明 |
| :--- | :---: | :---: | :--- |
| `MODAL_TOKEN_ID` | **是** | 无 | Modal 令牌 ID，从 [Modal 仪表盘](https://modal.com/settings) 获取 |
| `MODAL_TOKEN_SECRET` | **是** | 无 | Modal 令牌密钥 |
| `NEZHA_SERVER` | **是** | 无 | 哪吒v1填写形式: nezha.loc.cc:8008  哪吒v0填写形式：nezha.loc.cc |
| `NEZHA_KEY` | **是** | 无 | 哪吒v1的NZ_CLIENT_SECRET或哪吒v0的agent密钥 |
| `UUID` | 否 | b249d7ad-3331-4fc3-b1b4-d412fe0d4414 | 使用哪吒v1,在不同的平台运行需修改UUID,否则会覆盖 |
| `NEZHA_PORT` | 否 | 空 | 哪吒监控端口，若为空则根据 server 地址自动判断或使用默认端口 |
| `AUTO_ACCESS` | 否 | `true` | 是否自动访问保活（启用后将通过 `trans.ct8.pl` 添加定时访问任务） |
| `KEEPALIVE_INTERVAL` | 否 | `120` | 自访问保活请求间隔（秒） |

> **注意**：`PROJECT_URL` 无需配置，应用会在首次请求时自动检测。

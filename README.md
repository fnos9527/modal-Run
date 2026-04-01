
# Modal 哪吒探针部署 🚀

> ⭐ 觉得有用？点个 **Star** 支持一下！⭐

> 注册地址：https://modal.com

基于 **GitHub Actions** 一键部署 **Modal 哪吒探针**，支持 **V0 / V1**，支持 **全球 80+ 区域** 自由选择。

---

## 📋 目录

- [快速开始](#-快速开始)
- [Secrets 配置](#-secrets-配置)
- [工作流快捷输入](#-工作流快捷输入)
- [部署区域](#-部署区域)
- [API 调用](#-api-调用)
- [注意事项](#-注意事项)

---

## 🚀 快速开始

```
1. Fork 本仓库
2. 在仓库 Settings → Secrets and variables → Actions 中配置必填 Secrets
3. 进入 Actions → Modal 容器扎针 → Run workflow
4. 选择部署区域，点击运行
5. 等待部署完成，在哪吒面板查看节点上线
```

---

## 🔐 Secrets 配置

在仓库 **Settings → Secrets and variables → Actions** 中设置：

### 必填项

| Secret 名称 | 说明 | 格式示例 |
| :--- | :--- | :--- |
| `MODAL_TOKEN_ID` | Modal 令牌 ID，从 [Modal 仪表盘](https://modal.com/settings) 获取 | `ak-xxxxxxxxxxxxx` |
| `MODAL_TOKEN_SECRET` | Modal 令牌密钥 | `as-xxxxxxxxxxxxx` |
| `NEZHA_SERVER` | 哪吒服务器地址 | V1: `nezha.example.com:8008`<br>V0: `nezha.example.com` |
| `NEZHA_KEY` | 哪吒密钥 | V1: `NZ_CLIENT_SECRET`<br>V0: Agent 密钥 |

### 按版本必填

| Secret 名称 | 适用版本 | 说明 |
| :--- | :---: | :--- |
| `UUID` | **V1 必填** | 不同平台运行需修改 UUID，否则节点会被覆盖 |
| `NEZHA_PORT` | **V0 必填** | 哪吒监控端口，留空则自动判断 |

### 可选项

| Secret 名称 | 默认值 | 说明 |
| :--- | :---: | :--- |
| `AUTO_ACCESS` | `true` | 是否添加自动访问保活任务 |
| `KEEPALIVE_INTERVAL` | `120` | 自访问保活请求间隔（秒） |

> 💡 **提示**：`PROJECT_URL` 无需配置，应用会在首次请求时自动检测。

---

## ⚡ 工作流快捷输入

运行工作流时，可直接在界面填写以下参数，**无需修改 Secrets 即可临时覆盖**：

| 输入参数 | 说明 | 留空时行为 |
| :--- | :--- | :---: |
| `deploy_region` | 部署区域（下拉选择） | 默认 `us-east` |
| `modal_token_id` | Modal 令牌 ID | → 使用 Secret |
| `modal_token_secret` | Modal 令牌密钥 | → 使用 Secret |
| `nezha_server` | 哪吒服务器地址 | → 使用 Secret |
| `nezha_key` | 哪吒密钥 | → 使用 Secret |
| `uuid` | UUID（V1 必填） | → 使用 Secret |
| `nezha_port` | 哪吒端口（V0 必填） | → 使用 Secret |

```
优先级：工作流输入（非空） > Repository Secret
```

> 🎯 **典型场景**：多账号切换、临时测试不同区域、不想频繁修改 Secrets。

---

## 🌍 部署区域

支持全球 **80+ 区域**，涵盖 AWS / GCP / OCI / Azure 四大云平台。

> 📋 **API 调用时直接复制「选择值」列的内容作为 `deploy_region` 的值。**

<details>
<summary><b>🇺🇸 美国东部 US-EAST（9 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `us-east \| 美国东部（自动分配）` | 自动分配 |
| `us-east-1 \| AWS 弗吉尼亚州` | AWS 弗吉尼亚州 |
| `us-east-2 \| AWS 俄亥俄州` | AWS 俄亥俄州 |
| `us-east1 \| GCP 南卡罗来纳州` | GCP 南卡罗来纳州 |
| `us-east4 \| GCP 弗吉尼亚州` | GCP 弗吉尼亚州 |
| `us-east5 \| GCP 俄亥俄州` | GCP 俄亥俄州 |
| `us-ashburn-1 \| OCI 弗吉尼亚州` | OCI 弗吉尼亚州 |
| `eastus \| AZR 弗吉尼亚州` | AZR 弗吉尼亚州 |
| `eastus2 \| AZR 弗吉尼亚州2` | AZR 弗吉尼亚州 2 |

</details>

<details>
<summary><b>🇺🇸 美国中部 US-CENTRAL（8 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `us-central \| 美国中部（自动分配）` | 自动分配 |
| `us-central1 \| GCP 艾奥瓦州` | GCP 艾奥瓦州 |
| `us-chicago-1 \| OCI 芝加哥` | OCI 芝加哥 |
| `us-phoenix-1 \| OCI 凤凰城` | OCI 凤凰城 |
| `centralus \| AZR 艾奥瓦州` | AZR 艾奥瓦州 |
| `northcentralus \| AZR 伊利诺伊州` | AZR 伊利诺伊州 |
| `southcentralus \| AZR 德克萨斯州` | AZR 德克萨斯州 |
| `westcentralus \| AZR 怀俄明州` | AZR 怀俄明州 |

</details>

<details>
<summary><b>🇺🇸 美国南部 US-SOUTH（2 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `us-south \| 美国南部（自动分配）` | 自动分配 |
| `us-south1 \| GCP 达拉斯` | GCP 达拉斯 |

</details>

<details>
<summary><b>🇺🇸 美国西部 US-WEST（11 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `us-west \| 美国西部（自动分配）` | 自动分配 |
| `us-west-1 \| AWS 加利福尼亚` | AWS 加利福尼亚 |
| `us-west-2 \| AWS 俄勒冈州` | AWS 俄勒冈州 |
| `us-west1 \| GCP 俄勒冈州` | GCP 俄勒冈州 |
| `us-west2 \| GCP 洛杉矶` | GCP 洛杉矶 |
| `us-west3 \| GCP 盐湖城` | GCP 盐湖城 |
| `us-west4 \| GCP 拉斯维加斯` | GCP 拉斯维加斯 |
| `us-sanjose-1 \| OCI 圣何塞` | OCI 圣何塞 |
| `westus \| AZR 加利福尼亚` | AZR 加利福尼亚 |
| `westus2 \| AZR 华盛顿州` | AZR 华盛顿州 |
| `westus3 \| AZR 亚利桑那州` | AZR 亚利桑那州 |

</details>

<details>
<summary><b>🇪🇺 欧洲西部 EU-WEST（13 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `eu-west \| 欧洲西部（自动分配）` | 自动分配 |
| `eu-central-1 \| AWS 法兰克福` | AWS 法兰克福 |
| `eu-west-1 \| AWS 爱尔兰` | AWS 爱尔兰 |
| `eu-west-3 \| AWS 巴黎` | AWS 巴黎 |
| `europe-west1 \| GCP 比利时` | GCP 比利时 |
| `europe-west3 \| GCP 法兰克福` | GCP 法兰克福 |
| `europe-west4 \| GCP 荷兰` | GCP 荷兰 |
| `eu-frankfurt-1 \| OCI 法兰克福` | OCI 法兰克福 |
| `eu-paris-1 \| OCI 巴黎` | OCI 巴黎 |
| `westeurope \| AZR 荷兰` | AZR 荷兰 |
| `germanywestcentral \| AZR 法兰克福` | AZR 法兰克福 |
| `francecentral \| AZR 巴黎` | AZR 巴黎 |
| `polandcentral \| AZR 华沙` | AZR 华沙 |

</details>

<details>
<summary><b>🇪🇺 欧洲北部 EU-NORTH（5 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `eu-north \| 北欧（自动分配）` | 自动分配 |
| `eu-north-1 \| AWS 斯德哥尔摩` | AWS 斯德哥尔摩 |
| `northeurope \| AZR 爱尔兰` | AZR 爱尔兰 |
| `swedencentral \| AZR 瑞典` | AZR 瑞典 |
| `norwayeast \| AZR 奥斯陆` | AZR 奥斯陆 |

</details>

<details>
<summary><b>🇪🇺 欧洲南部 EU-SOUTH（5 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `eu-south \| 欧洲南部（自动分配）` | 自动分配 |
| `eu-south-1 \| AWS 米兰` | AWS 米兰 |
| `eu-south-2 \| AWS 西班牙` | AWS 西班牙 |
| `italynorth \| AZR 米兰` | AZR 米兰 |
| `spaincentral \| AZR 马德里` | AZR 马德里 |

</details>

<details>
<summary><b>🇨🇳 亚太东北 AP-NORTHEAST（10 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `ap-northeast \| 亚太东北（自动分配）` | 自动分配 |
| `ap-northeast-1 \| AWS 东京` | AWS 东京 |
| `ap-northeast-2 \| AWS 首尔` | AWS 首尔 |
| `ap-northeast-3 \| AWS 大阪` | AWS 大阪 |
| `asia-east1 \| GCP 台湾` | GCP 台湾 |
| `asia-northeast1 \| GCP 东京` | GCP 东京 |
| `asia-northeast3 \| GCP 首尔` | GCP 首尔 |
| `koreacentral \| AZR 首尔` | AZR 首尔 |
| `japaneast \| AZR 东京` | AZR 东京 |
| `japanwest \| AZR 大阪` | AZR 大阪 |

</details>

<details>
<summary><b>🇸🇬 亚太东南 AP-SOUTHEAST（5 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `ap-southeast \| 亚太东南（自动分配）` | 自动分配 |
| `ap-southeast-3 \| AWS 雅加达` | AWS 雅加达 |
| `asia-southeast1 \| GCP 新加坡` | GCP 新加坡 |
| `southeastasia \| AZR 新加坡` | AZR 新加坡 |
| `malaysiawest \| AZR 吉隆坡` | AZR 吉隆坡 |

</details>

<details>
<summary><b>🇮🇳 亚太南部 AP-SOUTH（7 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `ap-south \| 亚太南部（自动分配）` | 自动分配 |
| `ap-south-1 \| AWS 孟买` | AWS 孟买 |
| `asia-south1 \| GCP 孟买` | GCP 孟买 |
| `asia-south2 \| GCP 德里` | GCP 德里 |
| `centralindia \| AZR 浦那` | AZR 浦那 |
| `westindia \| AZR 孟买` | AZR 孟买 |
| `southindia \| AZR 金奈` | AZR 金奈 |

</details>

<details>
<summary><b>🇦🇺 澳大利亚 / 墨尔本（6 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `ap-melbourne \| 亚太墨尔本（自动分配）` | 自动分配 |
| `ap-melbourne-1 \| OCI 墨尔本` | OCI 墨尔本 |
| `au \| 澳大利亚（别名）` | 自动分配 |
| `australia-southeast1 \| GCP 悉尼` | GCP 悉尼 |
| `ap-sydney-1 \| OCI 悉尼` | OCI 悉尼 |
| `australiaeast \| AZR 悉尼` | AZR 悉尼 |

</details>

<details>
<summary><b>🇬🇧 英国 UK（6 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `uk \| 英国（自动分配）` | 自动分配 |
| `eu-west-2 \| AWS 伦敦` | AWS 伦敦 |
| `europe-west2 \| GCP 伦敦` | GCP 伦敦 |
| `uk-london-1 \| OCI 伦敦` | OCI 伦敦 |
| `uksouth \| AZR 伦敦` | AZR 伦敦 |
| `ukwest \| AZR 卡迪夫` | AZR 卡迪夫 |

</details>

<details>
<summary><b>🇨🇦 加拿大 CA（7 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `ca \| 加拿大（自动分配）` | 自动分配 |
| `ca-central-1 \| AWS 蒙特利尔` | AWS 蒙特利尔 |
| `northamerica-northeast2 \| GCP 多伦多` | GCP 多伦多 |
| `ca-toronto-1 \| OCI 多伦多` | OCI 多伦多 |
| `ca-montreal-1 \| OCI 蒙特利尔` | OCI 蒙特利尔 |
| `canadacentral \| AZR 多伦多` | AZR 多伦多 |
| `canadaeast \| AZR 魁北克` | AZR 魁北克 |

</details>

<details>
<summary><b>🌏 中东 / 南美 / 非洲 / 墨西哥 / 日本（13 个区域）</b></summary>

| 选择值 | 位置 |
| :--- | :--- |
| `me \| 中东（自动分配）` | 中东 自动分配 |
| `me-west1 \| GCP 特拉维夫` | GCP 特拉维夫 |
| `uaenorth \| AZR 迪拜` | AZR 迪拜 |
| `qatarcentral \| AZR 多哈` | AZR 多哈 |
| `sa \| 南美（自动分配）` | 南美 自动分配 |
| `sa-east-1 \| AWS 圣保罗` | AWS 圣保罗 |
| `southamerica-east1 \| GCP 圣保罗` | GCP 圣保罗 |
| `brazilsouth \| AZR 圣保罗` | AZR 圣保罗 |
| `af \| 非洲（自动分配）` | 非洲 自动分配 |
| `southafricanorth \| AZR 约翰内斯堡` | AZR 约翰内斯堡 |
| `mx \| 墨西哥（自动分配）` | 墨西哥 自动分配 |
| `mexicocentral \| AZR 墨西哥城` | AZR 墨西哥城 |
| `jp \| 日本（别名）` | 日本 自动分配 |

</details>

---

## 📡 API 调用

通过 GitHub API 触发工作流，适合自动化和多账号批量部署。

### 基础格式

```bash
curl -X POST \
  https://api.github.com/repos/{owner}/{repo}/actions/workflows/Modal.yml/dispatches \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token {your_github_token}" \
  -d '{
    "ref": "main",
    "inputs": {
      "deploy_region": "us-east | 美国东部（自动分配）",
      "modal_token_id": "",
      "modal_token_secret": "",
      "nezha_server": "",
      "nezha_key": "",
      "uuid": "",
      "nezha_port": ""
    }
  }'
```

### 调用示例

<details>
<summary><b>1️⃣ 最简调用 — 全部使用 Secret，默认区域</b></summary>

```bash
curl -X POST \
  https://api.github.com/repos/oyz8/modal-nz/actions/workflows/Modal.yml/dispatches \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_UBXXXXXXXXXf" \
  -d '{"ref":"main","inputs":{}}'
```

> 所有变量回退到 Secret，区域默认 `us-east`

</details>

<details>
<summary><b>2️⃣ 只改部署区域 — 其余用 Secret</b></summary>

```bash
curl -X POST \
  https://api.github.com/repos/oyz8/modal-nz/actions/workflows/Modal.yml/dispatches \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_UBXXXXXXXXXf" \
  -d '{
    "ref": "main",
    "inputs": {
      "deploy_region": "ap-northeast-1 | AWS 东京"
    }
  }'
```

</details>

<details>
<summary><b>3️⃣ 工作流输入覆盖全部变量</b></summary>

```bash
curl -X POST \
  https://api.github.com/repos/oyz8/modal-nz/actions/workflows/Modal.yml/dispatches \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_UBXXXXXXXXXf" \
  -d '{
    "ref": "main",
    "inputs": {
      "deploy_region": "asia-northeast1 | GCP 东京",
      "modal_token_id": "ak-xxxxxxxxxxxxxxxx",
      "modal_token_secret": "as-xxxxxxxxxxxxxxxx",
      "nezha_server": "nezha.example.com:8008",
      "nezha_key": "your-nezha-client-secret-here",
      "uuid": "a1b2c3d4-5678-9012-abcd-ef1234567890",
      "nezha_port": "5555"
    }
  }'
```

</details>

<details>
<summary><b>4️⃣ 只覆盖哪吒相关 — Modal 令牌用 Secret</b></summary>

```bash
curl -X POST \
  https://api.github.com/repos/oyz8/modal-nz/actions/workflows/Modal.yml/dispatches \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_UBXXXXXXXXXf" \
  -d '{
    "ref": "main",
    "inputs": {
      "deploy_region": "eu-west | 欧洲西部（自动分配）",
      "nezha_server": "nz.mysite.com:8008",
      "nezha_key": "my-nezha-v1-secret",
      "uuid": "11111111-2222-3333-4444-555555555555"
    }
  }'
```

> `modal_token_id`、`modal_token_secret`、`nezha_port` 未传 → 自动回退 Secret

</details>

<details>
<summary><b>5️⃣ 哪吒 V0 模式 — 需要指定端口</b></summary>

```bash
curl -X POST \
  https://api.github.com/repos/oyz8/modal-nz/actions/workflows/Modal.yml/dispatches \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_UBXXXXXXXXXf" \
  -d '{
    "ref": "main",
    "inputs": {
      "deploy_region": "us-west2 | GCP 洛杉矶",
      "nezha_server": "nezha.example.com",
      "nezha_key": "your-v0-agent-key",
      "nezha_port": "5555",
      "uuid": ""
    }
  }'
```

</details>

<details>
<summary><b>6️⃣ 多账号切换 — 不同 Modal 令牌</b></summary>

```bash
# 账号 A → 部署到东京
curl -X POST \
  https://api.github.com/repos/oyz8/modal-nz/actions/workflows/Modal.yml/dispatches \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_UBXXXXXXXXXf" \
  -d '{
    "ref": "main",
    "inputs": {
      "deploy_region": "ap-northeast-1 | AWS 东京",
      "modal_token_id": "ak-account-a-token-id",
      "modal_token_secret": "as-account-a-token-secret",
      "nezha_server": "nz.site-a.com:8008",
      "nezha_key": "secret-a",
      "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    }
  }'

# 账号 B → 部署到法兰克福
curl -X POST \
  https://api.github.com/repos/oyz8/modal-nz/actions/workflows/Modal.yml/dispatches \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token ghp_UBXXXXXXXXXf" \
  -d '{
    "ref": "main",
    "inputs": {
      "deploy_region": "eu-central-1 | AWS 法兰克福",
      "modal_token_id": "ak-account-b-token-id",
      "modal_token_secret": "as-account-b-token-secret",
      "nezha_server": "nz.site-b.com:8008",
      "nezha_key": "secret-b",
      "uuid": "ffffffff-1111-2222-3333-444444444444"
    }
  }'
```

</details>

### 参数速查表

| 参数名 | 必填 | 说明 | 留空行为 |
| :--- | :---: | :--- | :---: |
| `deploy_region` | 否 | 部署区域，需完整匹配 choice 选项 | 默认 `us-east` |
| `modal_token_id` | 否 | Modal 令牌 ID（`ak-` 开头） | → Secret |
| `modal_token_secret` | 否 | Modal 令牌密钥（`as-` 开头） | → Secret |
| `nezha_server` | 否 | V1: `host:8008` / V0: `host` | → Secret |
| `nezha_key` | 否 | 哪吒客户端密钥 | → Secret |
| `uuid` | 否 | V1 必填，不同平台需不同值 | → Secret |
| `nezha_port` | 否 | V0 必填，V1 留空 | → Secret |

---

## ⚠️ 注意事项

1. **区域值必须完整匹配** choice 选项中的格式：
   ```
   ✅ "ap-northeast-1 | AWS 东京"
   ❌ "ap-northeast-1"
   ❌ "东京"
   ```
2. **敏感信息安全**：通过 API `inputs` 传递的 token/key 可能出现在 Actions 日志中。生产环境建议优先使用 Secret，API 输入仅用于临时覆盖或测试。

3. **空值处理**：`inputs` 中传空字符串 `""` 等同于未传，会自动回退到 Secret。

4. **未传字段**：API 调用中未包含的 `inputs` 字段将使用工作流定义的默认值（空字符串），同样回退到 Secret。


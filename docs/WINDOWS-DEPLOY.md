# Windows 部署指南（Docker Desktop）

本 lab 的容器皆為 **Linux 映像**（Caldera、Suricata、Sandcat target）。在 Windows 上請使用 **Docker Desktop（WSL2 後端 + Linux containers）**，與 macOS 使用同一套 `compose.yml`，**不需要** Windows container 版本。

完整訓練與 NDR 說明見根目錄 [README.md](../README.md)。

---

## 前置需求

| 項目 | 說明 |
|------|------|
| Docker Desktop | 啟用 **WSL2**；設定為 **Linux containers**（非 Windows containers） |
| Git for Windows | 提供 `bash`，NDR cloud 啟動腳本需要 |
| Python 3.10+ | `trainingctl`、pytest |
| 記憶體 | 基礎 lab ≥ 4 GB；`up-ndr-cloud` 建議 ≥ 8 GB |
| 磁碟 | 首次 build 建議 ≥ 10 GB 可用空間 |

可選：在 WSL2 Ubuntu 內 clone repo，直接使用 `make`（與 Linux/macOS 相同）。

---

## 快速開始

### PowerShell（推薦）

```powershell
git clone https://github.com/ericmao/sensel-caldera-linux-lab.git
cd sensel-caldera-linux-lab
copy .env.example .env
# 編輯 .env；雲端 NDR 可複製 Portal bundle → ndr\portal.env

# 基礎 Caldera lab
.\scripts\windows\lab.ps1 up

# + inline Suricata（本機 NDR）
.\scripts\windows\lab.ps1 up-ndr

# + Edge Console :8090 + Portal 雲端報到
.\scripts\windows\lab.ps1 up-ndr-cloud

.\scripts\windows\lab.ps1 status-ndr-cloud
```

瀏覽器：

- Caldera：http://127.0.0.1:8888（預設 `red` / `admin`）
- Edge Console：http://127.0.0.1:8090（貼 Portal invite code）

### Git Bash / WSL2（與 Mac 相同）

```bash
cp .env.example .env
make validate
make up-ndr-cloud
```

---

## PowerShell 指令對照

| PowerShell | Make（Git Bash / WSL） |
|------------|-------------------------|
| `.\scripts\windows\lab.ps1 up` | `make up` |
| `.\scripts\windows\lab.ps1 up-ndr` | `make up-ndr` |
| `.\scripts\windows\lab.ps1 up-ndr-cloud` | `make up-ndr-cloud` |
| `.\scripts\windows\lab.ps1 down-ndr-cloud` | `make down-ndr-cloud` |
| `.\scripts\windows\lab.ps1 status-ndr-cloud` | `make status-ndr-cloud` |
| `.\scripts\windows\lab.ps1 validate` | `make validate` |
| `.\scripts\windows\lab.ps1 test` | `make test` |
| `.\scripts\windows\lab.ps1 clean` | `make clean` |

---

## `.env` 路徑範例（Windows）

```env
HEXSTRIKE_MCP_SCRIPT=C:/Users/you/hexstrike-ai/hexstrike_mcp.py
SENSEL_OT_EDGE_DIR=./vendor/sensel-ot-edge-sensor
SENSOR_ID=caldera-lab-ndr-win-01
OT_REGISTRATION_TOKEN=
```

Secrets 僅放 `.env` 或 `ndr\portal.env`（已 gitignore），勿 commit。

---

## 部署模式（Windows 適用性）

| 模式 | Windows Docker | 用途 |
|------|----------------|------|
| `up` | ✅ | Caldera 能力鏈訓練 |
| `up-ndr` | ✅ | inline Suricata，本機 `eve.json` |
| `up-ndr-cloud` | ✅ | Caldera 模擬 + Portal 註冊 smoke test |
| Ubuntu VM + Portal SPAN | ❌ 不在 Windows 上 | 正式 mirror 抓包請用 Ubuntu VM |

Windows 與 Mac 相同：**Docker 版適合 Caldera 模擬與雲端 Control Plane 整合測試**，不取代 SPAN 正式 NDR 感測器。

---

## 常見問題

| 問題 | 處理 |
|------|------|
| 無法執行 `.ps1` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `bash: command not found` | 安裝 Git for Windows，或改用 WSL2 |
| 腳本 `^M` / bad interpreter | `git config --global core.autocrlf input`；重新 checkout |
| 8888 / 8090 被占用 | `netstat -ano \| findstr :8090` |
| 建置極慢 | 首次 pull/build 正常；確認 Docker Desktop 已分配足夠 CPU/RAM |
| Portal 看不到 sensor | 需 `up-ndr-cloud` 並在 :8090 完成 invite；`up-ndr` 不連雲 |
| 切換到 Windows containers | 改回 **Linux containers**，否則無法跑本 lab |

---

## 安全提醒

- 僅 localhost 暴露 Caldera（`:8888`）與 Edge Console（`:8090`）
- target 容器無 privileged、無 host network
- edge 服務的 docker.sock 僅供 NDR 管理元件，不掛載至 target

---

## 相關文件

- [README.md](../README.md) — 完整架構、OT/IT NDR、場景
- [ndr/README.md](../ndr/README.md) — NDR 規則與拓撲
- [sensel-ot-edge-sensor](https://github.com/AvocadoAI-Lab/sensel-ot-edge-sensor) — Ubuntu SPAN 正式部署

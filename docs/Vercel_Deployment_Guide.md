# PolyAlpha Protocol — Vercel 部署指南

本指南將引導你將 PolyAlpha Protocol 的 React 前端部署到 Vercel，獲得一個公開的網址（如 `polyalpha.vercel.app`），方便期末 Demo 與展示。

## 為什麼選擇 Vercel？

Vercel 是目前最適合 React 應用的免費雲端託管平台。它的優勢在於：
- **與 GitHub 深度整合**：每次 `git push` 到 `main` 分支，Vercel 會自動重新部署
- **免費 SSL 憑證**：自動提供 HTTPS 加密連線
- **全球 CDN**：載入速度極快
- **無需伺服器管理**：不需處理 Nginx 或 Apache 設定

## 部署步驟

### 步驟 1：註冊 Vercel 帳號
1. 前往 [Vercel 官網](https://vercel.com/)
2. 點擊右上角的 **"Sign Up"**
3. 選擇 **"Continue with GitHub"**，並使用你的 GitHub 帳號（`YongWilliam-ai`）登入並授權

### 步驟 2：匯入 GitHub 儲存庫
1. 登入後，在 Vercel 控制台點擊 **"Add New..."** -> **"Project"**
2. 在 "Import Git Repository" 區塊中，找到 `YongWilliam-ai/polyalpha-protocol`
3. 點擊儲存庫旁邊的 **"Import"** 按鈕

### 步驟 3：配置部署設定
在 "Configure Project" 頁面中，請進行以下設定：

1. **Project Name**: 保持預設（如 `polyalpha-protocol`）或自訂（如 `polyalpha`）
2. **Framework Preset**: 確保選擇 **"Create React App"**（Vercel 通常會自動偵測到）
3. **Root Directory**: 點擊 "Edit"，選擇 `frontend` 資料夾（**這一步非常重要！** 因為你的 React 程式碼在 `frontend` 資料夾內，而不是根目錄）
4. **Build and Output Settings**: 保持預設不變
   - Build Command: `npm run build`
   - Output Directory: `build`
5. **Environment Variables**: 目前前端如果是連接本地的 ChainLab Testnet，可以先不填。後續如果部署到公網測試鏈，再將 RPC URL 加進來。

### 步驟 4：點擊 Deploy
1. 點擊 **"Deploy"** 按鈕
2. 等待約 1-2 分鐘，Vercel 會自動下載相依套件並建立你的 React 應用
3. 看到滿天撒花的動畫，代表部署成功！

## Demo 時的注意事項

由於你的智能合約目前部署在本地的 ChainLab Testnet（chainId: 31337）：

1. **MetaMask 設定**：Demo 時，展示用的電腦的 MetaMask 必須連接到相同的本地網路（RPC URL: `http://127.0.0.1:8545`）。
2. **合約互動**：Vercel 上的前端網站可以與你本地運行的 Hardhat 節點互動，前提是兩者都在同一台電腦上執行，或者 Hardhat 節點的 RPC 端口有對外開放。
3. **靜態展示**：如果只是展示 UI，即使沒有連接到本地節點，網站也能正常顯示（雖然數據可能是 0 或載入中）。

## 更新網站
部署完成後，只要你在本地修改了前端程式碼並執行：
```bash
git add -A
git commit -m "update UI"
git push origin main
```
Vercel 就會自動抓取最新程式碼並更新你的網站，完全不需要手動操作。

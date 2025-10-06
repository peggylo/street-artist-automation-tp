# 台北街頭藝人場地申請自動化系統 開發指南

## 🎯 開發原則
- **最小化開發**：核心功能優先，避免過度設計
- **分段驗證**：每階段都要測試，確認無誤再進下一階段

---

## 📁 專案架構

```
street-artist-automation-tp/
├── docs/                           # 專案文件
│   ├── PRD.md                     # 產品需求文件
│   ├── development-guide.md       # 開發指南（本文件）
│   ├── browser-automation-guide.md # 瀏覽器自動化反檢測指南
│   └── template/                  # 文件範本
├── gas-webhook/                    # Google Apps Script（未來功能）
│   └── config.gs                  # GAS 設定檔
├── github-automation/              # 自動化程式碼（目前位置）
│   ├── main.py                    # 核心申請邏輯 (Playwright)
│   ├── anti_detection.py          # 反檢測技術模組
│   ├── storage_handler.py         # 截圖儲存處理（GCS 上傳）
│   ├── config.py                  # 設定檔（網站 URL、Phase 控制）
│   ├── requirements.txt           # Python 依賴套件
│   └── screenshots/               # 本機開發時的截圖（不上傳 Git）
├── cloud-run/                      # Cloud Run 部署設定
│   ├── Dockerfile                 # Docker 建置檔
│   ├── entrypoint.sh              # 容器啟動腳本（診斷版）
│   ├── deploy.sh                  # 部署腳本
│   ├── cloudbuild.yaml            # Cloud Build 設定
│   └── .dockerignore              # Docker 忽略檔案
└── .gitignore                      # Git 忽略檔案設定
```

**📝 重構計畫說明：**  
目前 `main.py`、`anti_detection.py`、`storage_handler.py` 等核心程式碼放在 `github-automation/` 目錄下，但這些其實是各 Phase 共用的程式碼，不應該放在特定平台的目錄中。

**未來重構方向：**
- 建立 `src/` 或 `automation/` 目錄存放共用程式碼
- `github-automation/` 只保留 GitHub Actions 特定的 workflow 檔案
- `cloud-run/` 只保留 Cloud Run 特定的部署檔案
- 各平台透過相對路徑引用共用程式碼

**延後原因：** 等 Headless 模式成功突破 reCAPTCHA 後再進行重構，目前先專注於解決核心技術問題。

---

## 🔄 系統資料流程

1. **LINE 申請** → GAS 接收訊息並立即觸發處理
2. **GAS 處理**：
   - 寫入申請記錄到 Google Sheets（純記錄用途）
   - 立即呼叫 GitHub Actions API，傳遞 `timestamp` + `apply_period` + `chat_id`
3. **GitHub Actions 執行**：
   - 接收參數，執行 Playwright 申請流程
   - 自動點擊所有「個人登記」按鈕申請可用時段
   - 完成後透過 timestamp 比對，更新對應的 Sheets 記錄
4. **結果通知**：GitHub Actions 直接透過 `chat_id` 發送結果與截圖到原始申請的聊天室（群組或個人），成功時包含具體登記時段詳情
5. **錯誤處理**：所有失敗都自動重試 3 次，間隔 30 秒

---

## 🚀 開發階段

**階段說明：**
- **階段 A-B-D**：LINE Bot、Sheets、系統整合（尚未開發）
- **階段 C**：瀏覽器自動化與雲端部署（🔧 進行中）
  - Phase 1-4 代表不同的執行環境（本地/雲端、有頭/無頭）
  - 詳細進度請見文末「專案當前狀態總結」

---

### 階段 A: LINE Bot 基礎設定 ⏸️ 未開始

#### 範疇
- 核心：LINE Bot 申請、Google Apps Script Webhook 設定
- 核心：申請時間窗口檢查邏輯
- 不做：複雜對話邏輯，僅處理基本申請需求

#### 技術決策
- **LINE Bot**：LINE Messaging API - 免費額度足夠，官方支援完整
- **中介系統**：Google Apps Script - 免費、無需維護、整合 Google 服務容易
- **敏感資訊管理**：GitHub Actions Environment secrets
- **表演項目填寫**：「本次展演項目」欄位填入「唱歌、跳舞、助盲」（手動輸入，非選項）

#### 開發任務
- [ ] 申請 LINE Bot (Channel Access Token, Channel Secret)
- [ ] 建立 Google Apps Script 專案
- [ ] 設定 LINE Webhook 指向 GAS
- [ ] 實作 GAS 基本訊息接收功能
- [ ] 實作申請時間窗口檢查邏輯

#### 階段驗證
- [ ] 媽媽發 LINE 訊息，GAS 能收到並回覆
- [ ] 申請期間內外的不同回應正常
- [ ] 基本訊息解析功能正常

### 階段 B: Google Sheets 整合 ⏸️ 未開始

#### 範疇
- 核心：建立申請記錄表、實作資料新增更新功能
- 核心：GAS 立即觸發 GitHub Actions，不依賴 Sheets 讀取
- 不做：複雜的資料分析，僅記錄基本申請流程

#### 技術決策
- **資料儲存**：Google Sheets - 免費、易查看、與 GAS 整合簡單

#### 開發任務
- [ ] 建立 Google Sheets 申請記錄表（依照下方欄位規格）
- [ ] GAS 新增申請記錄到 Sheets
- [ ] GAS 立即觸發 GitHub Actions API（傳遞 timestamp + apply_period + chat_id）
- [ ] 測試 GAS 與 Sheets 資料操作功能

#### 階段驗證
- [ ] 能正確新增申請記錄到 Sheets
- [ ] 能立即觸發 GitHub Actions 並傳遞必要參數
- [ ] Sheets 作為記錄查看正常運作

### 階段 C: 瀏覽器自動化與雲端部署 🔧 進行中

**目標：** 開發完整的瀏覽器自動化申請流程，並部署到雲端環境

**執行環境（Phase 1-4）：**
- Phase 1: 本地有頭模式 ✅ 成功
- Phase 2: 本地無頭模式 ❌ 失敗
- Phase 3: GitHub Actions ❌ 失敗
- Phase 4: Cloud Run Jobs ❌ 失敗

#### 範疇
- 核心：開發完整的網站自動申請流程
- 核心：實作反檢測技術（Profile 管理、養軌跡、行為模擬）
- 核心：支援多種執行環境（本地/雲端、有頭/無頭）
- 核心：截圖功能與雲端儲存整合

#### 技術決策
- **自動化工具**：Playwright - 比 Selenium 更穩定快速，適合政府網站
- **開發環境**：本機開發 - 除錯方便，測試快速
- **程式架構**：採用單一程式架構 - 直接在 main.py 中處理網站結構識別和自動化操作
- **反檢測策略**：詳細瀏覽器自動化反檢測策略請參考 `browser-automation-guide.md`
- **申請策略**：登入後自動點擊所有「個人登記」按鈕申請可用時段（無優先順序，有「個人登記」選項即為可申請，全部時段都申請）
- **成功判斷**：彈跳視窗顯示「個人登記(需管理者審核通過)完成!」，按確定後等待5秒回到日曆頁面
- **失敗策略**：任何一個時段申請失敗就算整體失敗，全部完成後才截圖
- **申請截止時間**：開放窗口最後一天的 17:00 前（不包含 17:00）
  - 例如：10/1-3 申請期間，10/1 晚上 23:00 申請仍可，但 10/3 17:00 後就不行

#### 開發任務（已完成）
採用單一程式架構，直接在 main.py 中整合所有功能：

**第一階段：環境設定與基礎功能**
- [x] 本機安裝 Playwright 環境
- [x] 開發 `main.py` - 整合網站結構識別和自動化執行
- [x] 實作登入流程（固定流程：確定登入 → 台北通 → 帳密輸入）

**第二階段：核心自動化功能**
- [x] 實作場地選擇邏輯（支援多個場地）
- [x] 實作自動識別可申請時段功能（尋找所有「個人登記」按鈕並全部申請）
- [x] 實作表演項目填寫（在「本次展演項目」欄位填入「唱歌、跳舞、助盲」）
- [x] 處理成功彈跳視窗（按確定 → 等待5秒 → 回到日曆頁面）

**第三階段：整合測試**
- [x] 加入截圖功能並測試（全部完成後截圖）
- [x] 本機完整流程測試
- [x] 錯誤處理與重試機制測試
- [x] 反檢測技術實作（Profile 管理、養軌跡、行為模擬）

#### 各 Phase 測試結果

| Phase | 環境 | 核心功能 | reCAPTCHA | 備註 |
|-------|------|----------|-----------|------|
| **Phase 1** | 本地有頭 | ✅ 完整 | ✅ 通過 | 唯一成功的環境 |
| **Phase 2** | 本地無頭 | ✅ 完整 | ❌ 失敗 | 被識別為機器人 |
| **Phase 3** | GitHub Actions | ✅ 完整 | ❌ 失敗 | 含 xvfb、截圖上傳 |
| **Phase 4** | Cloud Run Jobs | ✅ 完整 | ❌ 失敗 | 含 GCS 上傳、日誌輸出 |

**Phase 4 部署指令：**
```bash
./cloud-run/deploy.sh                                          # 部署
gcloud run jobs execute street-artist-job --region asia-east1  # 執行
```

#### 技術限制
- ❌ **reCAPTCHA v3 瓶頸**：只有 Phase 1（本地有頭）能通過，其他全部失敗
- 📚 **詳細分析**：參考 `browser-automation-guide.md`

---

### 階段 D: 完整系統整合 ⏸️ 未開始

**目標：** 串接所有系統元件，實現完整的自動化流程

#### 範疇
- 核心：LINE Bot + GAS + 自動化程式 + Sheets 記錄
- 核心：自動觸發、執行、回報結果
- 核心：錯誤處理與重試機制

#### 技術決策
- **觸發機制**：GAS 接收 LINE 訊息後觸發自動化程式
- **通知機制**：執行結果透過 LINE 回傳（包含截圖）

#### 開發任務（待階段 C 解決 reCAPTCHA 後進行）
- [ ] GAS 觸發機制
- [ ] 接收參數與更新 Sheets
- [ ] 結果通知與截圖傳送
- [ ] 端到端測試

#### 階段驗證
- [ ] 完整流程：LINE 申請 → 自動處理 → 結果通知
- [ ] Google Sheets 正確記錄
- [ ] 媽媽收到結果通知

---

## 🔐 環境變數與敏感資訊管理

### 各 Phase 敏感資訊管理方式

| Phase | 環境 | 管理方式 | 說明 |
|-------|------|----------|------|
| **Phase 1** | 本地開發 | `.env` 檔案 | 本機測試用，不上傳到 Git |
| **Phase 2** | 本地 Headless | `.env` 檔案 | 同 Phase 1 |
| **Phase 3** | GitHub Actions | Repository Secrets | GitHub 內建加密儲存 |
| **Phase 4** | Cloud Run Jobs | Secret Manager | GCP 雲端加密儲存 |

**必要變數（Phase 1-4 通用）：**
- `TAIPEI_USERNAME` - 台北市街頭藝人網站登入帳號
- `TAIPEI_PASSWORD` - 台北市街頭藝人網站登入密碼

---

### 階段 D: Google Apps Script 設定（未來整合）

**設定位置**：Google Apps Script > 專案設定 > 指令碼屬性

| 屬性名稱 | 說明 |
|---------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot Token |
| `LINE_CHANNEL_SECRET` | LINE Bot Secret |
| `GITHUB_TOKEN` | GitHub Personal Access Token |

### 安全性注意事項

- **絕不在程式碼中寫入敏感資訊**
- **使用環境變數或指令碼屬性讀取**
- **定期更新 Token 和密碼**
- **限制 Service Account 最小權限**

---

## 📊 Google Sheets 欄位規格

**重要**：程式必須使用欄位名稱而非欄位編號來識別資料，因為欄位順序可能調整。

| 欄位名稱 | 格式/範例 | 說明 |
|---------|-----------|------|
| **時間戳記** | 20250914-114803 | 收到 LINE 申請的時間 |
| **用戶ID** | U1234567890abcdef | LINE 用戶 ID |
| **聊天室ID** | U1234567890abcdef 或 C1234567890abcdef | 申請來源的聊天室ID（個人或群組） |
| **申請期間** | 2025-10上半月 | 申請的目標時段 |
| **狀態** | 待處理/處理中/已完成/失敗 | 當前處理狀態 |
| **錯誤訊息** | 網站問題-連線逾時30秒 | 失敗原因分類-詳細錯誤訊息 |
| **登記時段** | 2026/1/14 (二) 早上、下午、晚上；2026/1/5 (日) 早上、晚上 | 成功登記的具體時段（含星期與時段名稱） |
| **處理開始時間** | 20250914-114803 | 系統開始執行時間 |
| **處理完成時間** | 20250914-114856 | 成功完成時間（失敗時空白） |
| **截圖** | Google Drive 連結 | 成功：完成畫面，失敗：錯誤畫面 |

**錯誤分類建議**：
- 網站問題：無法訪問、載入失敗
- 申請被拒絕：時段已滿、不符資格  
- 系統異常：程式錯誤、意外中斷
- 網路問題：連線逾時、暫時性問題
- 其他：直接描述具體錯誤內容

---

## 🔧 已解決與未解決問題記錄

### ✅ 已解決問題

#### Cloud Run Jobs 日誌輸出問題 - 2025-10-06
**症狀**：Cloud Run Jobs 執行後完全沒有日誌輸出  
**原因**：xvfb-run 預設不轉發 stdout/stderr，Python 輸出緩衝  
**解決**：建立 `entrypoint.sh` 診斷腳本（環境檢查、Xvfb 背景啟動）、所有 Python 模組加入 `flush=True` 輸出追蹤、修正 `.dockerignore` 允許腳本複製  
**成果**：✅ Cloud Logging 完整輸出，可追蹤每個執行步驟

---

### ❌ 未解決問題

#### reCAPTCHA v3 反機器人檢測 - 2025-10-06
**症狀**：Headless 模式（Phase 2-4）全部被識別為機器人，無法登入  
**原因**：reCAPTCHA v3 使用機器學習分析行為，Headless 瀏覽器缺少真實特徵（WebGL、Canvas 等）  
**可能方案**：
1. 真實瀏覽器 VPS（成本較高）
2. 第三方驗證碼服務（如 2Captcha，需付費）
3. 改為手動或半自動化
4. 等待網站改版

**詳細分析**：參考 `browser-automation-guide.md`


---

## 📊 專案當前狀態總結（2025-10-06）

### 開發進度
- ⏸️  **階段 A-B**：LINE Bot、Sheets - 未開始
- 🔧 **階段 C**：瀏覽器自動化與雲端部署 - 進行中
  - ✅ Phase 1（本地有頭）：完全成功
  - ❌ Phase 2-4（Headless）：受 reCAPTCHA 阻擋
- ⏸️ **階段 D**：完整系統整合 - 未開始

### 關鍵成就與限制
✅ **已完成**：自動化核心功能、反檢測技術、多環境部署（Phase 1-4）  
❌ **受阻**：reCAPTCHA v3 - Headless 模式全部失敗，無法在雲端無人值守環境執行

### 下一步選項
1. 只使用 Phase 1 本地執行（需要有畫面的環境）
2. 付費解決：第三方驗證碼服務或桌面環境 VPS
3. 改為手動或半自動化流程
4. 等待網站改版或新技術突破

---

**版本**: v2.1 | **更新**: 2025-10-06 | **狀態**: 階段 C 進行中（Phase 1 成功，Phase 2-4 受限）
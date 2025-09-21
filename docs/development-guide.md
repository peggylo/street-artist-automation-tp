# 台北街頭藝人場地申請自動化系統 開發指南

## 🎯 開發原則
- **最小化開發**：核心功能優先，避免過度設計
- **分段驗證**：每階段都要測試，確認無誤再進下一階段

---

## 📁 專案架構

```
street-artist-automation-tp/
├── docs/                           # 專案文件
│   ├── PRD.md
│   ├── development-guide.md
│   └── template/
├── gas-webhook/                     # Google Apps Script
│   ├── main.gs                     # 全部 GAS 功能（LINE Webhook + Sheets + GitHub 觸發）
│   └── config.gs                   # 一般設定（Sheets ID、場地選項）
├── github-automation/               # GitHub Actions 自動化
│   ├── main.py                     # 核心申請邏輯 (Playwright)
│   ├── config.py                   # 一般設定（網站 URL、重試次數）
│   ├── google_services.py          # Google API 整合 (Sheets/Drive)
│   ├── line_bot.py                 # LINE Bot 通知功能
│   ├── requirements.txt            # Python 依賴套件
│   ├── screenshots/                # 本機開發時的截圖存放資料夾（不上傳 Git）
│   └── .github/
│       └── workflows/
│           └── apply.yml           # GitHub Actions 工作流程
└── .gitignore                      # Git 忽略檔案設定
```

**注意**：此架構為初期規劃，隨著開發進行仍有調整可能。

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
4. **結果通知**：GitHub Actions 直接透過 `chat_id` 發送結果與截圖到原始申請的聊天室（群組或個人）
5. **錯誤處理**：所有失敗都自動重試 3 次，間隔 30 秒

---

## 🚀 開發階段

### Phase 1: LINE Bot 基礎設定

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

### Phase 2: Google Sheets 整合

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

### Phase 3: 本機 Playwright 開發

#### 範疇
- 核心：在本機開發完整的網站自動申請流程
- 核心：截圖功能與本機測試
- 核心：自動識別並申請所有可用時段

#### 技術決策
- **自動化工具**：Playwright - 比 Selenium 更穩定快速，適合政府網站
- **開發環境**：本機開發 - 除錯方便，測試快速
- **申請策略**：登入後自動點擊所有「個人登記」按鈕申請可用時段（無優先順序，有「個人登記」選項即為可申請）
- **申請截止時間**：開放窗口最後一天的 17:00 前（不包含 17:00）
  - 例如：10/1-3 申請期間，10/1 晚上 23:00 申請仍可，但 10/3 17:00 後就不行

#### 開發任務
- [ ] 本機安裝 Playwright 環境
- [ ] 開發登入流程（帳號密碼輸入）
- [ ] 實作場地選擇邏輯（大安森林公園2號出口）
- [ ] 實作自動識別可申請時段功能（尋找「個人登記」按鈕）
- [ ] 實作表演項目填寫（在「本次展演項目」欄位填入「唱歌、跳舞、助盲」）
- [ ] 加入截圖功能並測試
- [ ] 本機完整流程測試

#### 階段驗證
- [ ] 能成功登入台北市街頭藝人申請網站
- [ ] 能正確選擇大安森林公園場地
- [ ] 能自動識別並申請所有可用時段
- [ ] 申請完成後能截圖儲存

### Phase 4: GitHub Actions 部署

#### 範疇
- 核心：將本機程式移植到 GitHub Actions
- 核心：雲端環境測試與 Google Drive 整合

#### 技術決策
- **執行平台**：GitHub Actions - 完全免費，部署簡單
- **截圖儲存**：Google Drive - 與現有 Google 服務整合

#### 開發任務
- [ ] 建立 GitHub Actions 工作流程檔案
- [ ] 設定環境變數（帳號密碼、API 金鑰）
- [ ] 移植本機 Playwright 程式到雲端
- [ ] 整合 Google Drive 截圖上傳功能
- [ ] 雲端環境測試

#### 階段驗證
- [ ] GitHub Actions 能成功執行申請流程
- [ ] 截圖能正確上傳到 Google Drive
- [ ] 雲端與本機執行結果一致

### Phase 5: 完整系統整合

#### 範疇
- 核心：串接所有系統元件，完整流程測試
- 核心：LINE Bot 圖片傳送與錯誤處理

#### 技術決策
- **觸發機制**：GAS 呼叫 GitHub Actions API - 即時觸發，傳遞 timestamp + apply_period + chat_id
- **通知機制**：GitHub Actions 直接透過 chat_id 發送結果到原始聊天室 - 使用者體驗最佳

#### 開發任務
- [ ] GAS 觸發 GitHub Actions API 功能
- [ ] GitHub Actions 接收參數（timestamp + apply_period + chat_id）
- [ ] GitHub Actions 更新 Sheets 申請結果（透過 timestamp 比對）
- [ ] GitHub Actions 直接透過 chat_id 發送結果到原始聊天室功能
- [ ] 完整錯誤處理與重試機制
- [ ] 端到端完整流程測試

#### 階段驗證
- [ ] 完整流程測試：LINE 申請 → 自動處理 → 結果通知
- [ ] Google Sheets 正確記錄申請與結果
- [ ] 媽媽能收到包含截圖的結果通知

---

## 🔐 環境變數與敏感資訊管理

### GitHub Actions Environment Secrets

**設定位置**：GitHub Repository > Settings > Secrets and variables > Actions

**設定時機**：Phase 4 - GitHub Actions 部署階段

| 變數名稱 | 說明 | 範例 |
|---------|------|------|
| `TAIPEI_ARTIST_USERNAME` | 台北市街頭藝人網站登入帳號 | 實際帳號 |
| `TAIPEI_ARTIST_PASSWORD` | 台北市街頭藝人網站登入密碼 | 實際密碼 |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Google Service Account JSON 金鑰 | 完整 JSON 內容 |
| `GOOGLE_SHEETS_ID` | Google Sheets 試算表 ID | 從 Google Sheets URL 取得 |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Drive 截圖資料夾 ID | 從 Google Drive 資料夾 URL 取得 |

### Google Apps Script 指令碼屬性

**設定位置**：Google Apps Script > 專案設定 > 指令碼屬性

**設定時機**：Phase 1 - LINE Bot 基礎設定階段

| 屬性名稱 | 說明 | 範例 |
|---------|------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot Channel Access Token | 實際 Token |
| `LINE_CHANNEL_SECRET` | LINE Bot Channel Secret | 實際 Secret |
| `GITHUB_TOKEN` | GitHub Personal Access Token | ghp_xxxxxxxxxxxx |

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
| **登記時段** | 2026/1/14 早下晚、2026/1/5 早晚 | 成功登記的具體時段 |
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

## 🔧 已解決問題記錄

### 架構選擇 - 2025-09-20
**症狀**：Cloud Run 部署時間過長影響開發效率
**原因**：每次容器打包部署需要6-10分鐘
**解決**：改用 GitHub Actions，git push 即部署，2分鐘內執行
**預防**：優先選擇開發友善的無伺服器解決方案

### 成本控制 - 2025-09-20
**症狀**：擔心雲端服務費用過高
**原因**：使用頻率低（每月僅2次），持續運行的伺服器浪費資源
**解決**：採用按需執行架構，所有服務都在免費額度內
**預防**：選擇服務前先評估實際使用量

---

**版本**: v1.0 | **更新**: 2025-09-20
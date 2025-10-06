# 瀏覽器自動化反檢測指南

## 🎯 目標與背景

台北通登入系統使用 reCAPTCHA v3 檢測機器人行為，直接使用 Playwright 自動化容易被識別並阻擋登入。本指南提供完整的反檢測策略，確保自動化程式能穩定通過人機驗證。

## 🏗️ 整體策略架構

### 核心理念
**模擬真實用戶的完整瀏覽歷程**，而非僅針對登入頁面進行自動化操作。

### 三階段防護
1. **環境偽裝**：使用臨時 Profile 避免自動化標識
2. **行為養成**：預先瀏覽相關網站建立真實軌跡  
3. **操作自然化**：模擬人類的點擊、輸入、移動行為

---

## 📂 Profile 管理策略

### 統一使用臨時 Profile 方案

**本機開發與 GitHub Actions 完全一致**

#### 為什麼選擇臨時 Profile？
- **環境一致性**：本機測試結果等同雲端執行結果
- **真實性**：每次都是「全新用戶」體驗，符合真實情境
- **乾淨性**：無殘留資料影響，問題容易重現
- **安全性**：不會洩漏個人瀏覽資料

#### Profile 生命週期
1. **程式啟動**：建立臨時資料夾 `/tmp/street-artist-profile-[隨機數字]/`
2. **執行期間**：所有瀏覽器資料儲存於此
3. **程式結束**：自動清理刪除資料夾

---

## 🎪 養軌跡策略

### 瀏覽路徑設計

**目標**：建立「準備申請街頭藝人」的真實用戶軌跡

#### 建議瀏覽順序
1. **台北市政府首頁** (taipei.gov.tw)
   - 停留 15-25 秒
   - 輕微滾動頁面

2. **市民服務專區**
   - 停留 20-30 秒  
   - 點擊 1-2 個相關連結

3. **線上申辦服務**
   - 停留 15-20 秒
   - 瀏覽申辦項目列表

4. **文化局相關頁面**（可選）
   - 停留 10-15 秒

#### 時間分配
- **總計時間**：2-3 分鐘
- **頁面間隔**：5-10 秒隨機延遲
- **考量因素**：平衡真實性與執行效率

---

## 🤖 反檢測技術

### 瀏覽器啟動參數

**移除自動化標識**
- 停用自動化控制特徵
- 模擬真實用戶代理
- 關閉開發者工具檢測

### 行為模擬技術

#### 登入階段（高強度模擬）
- **滑鼠移動**：模擬真實軌跡，避免直線移動
- **點擊行為**：隨機偏移點擊位置
- **文字輸入**：逐字輸入，隨機打字速度
- **操作間隔**：隨機延遲 100-300ms

#### 登入後階段（中強度模擬）  
- **基本延遲**：操作間隔 50-150ms
- **自然點擊**：點擊前短暫停留
- **表單填寫**：逐字輸入表演項目

---

## 🔄 錯誤處理與重試機制

### 重試策略

**被 reCAPTCHA 阻擋時的處理**
1. **完全重建**：刪除當前 Profile，建立全新環境
2. **重新養軌跡**：執行完整的瀏覽歷程
3. **延長等待**：增加操作間隔時間
4. **最大重試**：3 次，間隔 30 秒

### 失敗判斷標準
- 登入頁面出現「機器人驗證未通過」訊息
- 登入按鈕點擊後無反應超過 30 秒
- 頁面跳轉到錯誤或驗證頁面

---

## 🖥️ 開發環境配置

### 本機開發階段

#### Phase 1：有畫面除錯 ✅ 成功
- **瀏覽器模式**：headless=False
- **目的**：觀察每個步驟，確認流程正確
- **Profile**：臨時資料夾
- **養軌跡**：完整執行
- **狀態**：✅ **成功通過 reCAPTCHA 驗證**
- **原因**：真實瀏覽器環境，完整的用戶行為特徵

#### Phase 2：無畫面測試 ❌ 失敗
- **瀏覽器模式**：headless=True（透過 config.py 控制）
- **目的**：模擬 GitHub Actions 環境，為 xvfb 做準備
- **反檢測增強**：
  - User-Agent 改為 Linux 版本
  - 增強 headless 反檢測參數
  - 適度調整人類行為模擬參數
- **養軌跡**：維持 2-3 分鐘（TRAJECTORY_BUILDING_ENABLED=True）
- **截圖機制**：維持現有密度，每個步驟自動截圖
- **狀態**：❌ **被 reCAPTCHA 識別為機器人**
- **原因**：Headless 模式缺少真實瀏覽器特徵，即使有反檢測措施仍被識別

#### Phase 3：GitHub Actions 部署 ❌ 失敗

**核心策略：GitHub Actions + xvfb 虛擬顯示器**

##### 環境特性
- **執行環境**：Ubuntu Linux
- **顯示方式**：xvfb 虛擬螢幕
- **Profile 位置**：/tmp/ 臨時目錄
- **網路環境**：GitHub Actions IP 範圍
- **User-Agent**：Linux 版本

##### 敏感資訊管理
- **Repository Secrets**：
  - `TAIPEI_USERNAME`: 台北通帳號
  - `TAIPEI_PASSWORD`: 台北通密碼
- **config.py**：改用 `os.getenv()` 讀取環境變數

##### 截圖策略
- **執行期間**：截圖存儲在虛擬機本機
- **執行完畢**：自動上傳到 GitHub Artifacts

##### xvfb 設定
```yaml
- name: Install xvfb
  run: sudo apt-get install -y xvfb

- name: Run with xvfb
  env:
    TAIPEI_USERNAME: ${{ secrets.TAIPEI_USERNAME }}
    TAIPEI_PASSWORD: ${{ secrets.TAIPEI_PASSWORD }}
    PHASE: 3
  run: |
    cd github-automation
    xvfb-run -a python main.py
```

**狀態**：❌ **被 reCAPTCHA 識別為機器人**
**原因**：即使使用 xvfb，仍在 headless 環境執行，缺少真實瀏覽器特徵

#### Phase 4：Cloud Run Jobs 部署 ❌ 失敗

**核心策略：GCP Cloud Run Jobs + xvfb + GCS 截圖上傳**

##### 環境特性
- **執行環境**：Docker Container (Debian Linux)
- **顯示方式**：Xvfb 虛擬顯示器
- **Profile 位置**：/tmp/ 臨時目錄
- **截圖上傳**：即時上傳到 Google Cloud Storage
- **日誌系統**：Cloud Logging（已完全解決日誌輸出問題）

##### 敏感資訊管理
- **Secret Manager**：
  - `TAIPEI_USERNAME`: 台北通帳號
  - `TAIPEI_PASSWORD`: 台北通密碼
- **Service Account**: 具有 Secret Manager 和 Storage Admin 權限

##### 部署與執行
```bash
# 部署
./cloud-run/deploy.sh

# 執行
gcloud run jobs execute street-artist-job --region asia-east1

# 查看日誌
gcloud logging read "resource.type=cloud_run_job ..."
```

##### 日誌輸出改進（已解決）
- ✅ 使用 `entrypoint.sh` 診斷腳本
- ✅ Xvfb 在背景啟動，不透過 xvfb-run
- ✅ 完整的環境診斷和模組載入追蹤
- ✅ 所有 stdout/stderr 正確輸出到 Cloud Logging
- 📚 詳細說明：參考 `development-guide.md` 的「已解決問題」章節

**狀態**：❌ **被 reCAPTCHA 識別為機器人**
**原因**：
1. Headless 環境執行，缺少真實瀏覽器特徵
2. 無法使用 `channel="chrome"`（改用 Playwright Chromium）
3. reCAPTCHA v3 偵測到自動化行為模式



---

## 📊 各 Phase 測試結果總結（2025-10-06）

| Phase | 環境 | Headless | 狀態 | 備註 |
|-------|------|----------|------|------|
| Phase 1 | 本地 macOS | ❌ False | ✅ 成功 | 真實瀏覽器環境，完整用戶特徵 |
| Phase 2 | 本地 macOS | ✅ True | ❌ 失敗 | Headless 缺少瀏覽器特徵 |
| Phase 3 | GitHub Actions | ✅ True + xvfb | ❌ 失敗 | 虛擬顯示器仍被識別 |
| Phase 4 | Cloud Run | ✅ True + Xvfb | ❌ 失敗 | Container 環境被識別 |

### 關鍵發現

**✅ 成功要素（Phase 1）：**
- 真實的桌面瀏覽器環境
- 完整的瀏覽器指紋特徵
- 真實的用戶交互模式

**❌ 失敗要素（Phase 2-4）：**
- Headless 模式本質缺陷
- 缺少真實瀏覽器的 WebGL、Canvas 等特徵
- reCAPTCHA v3 的行為分析偵測
- 虛擬顯示器無法提供真實環境特徵

### 技術債務與限制

**已解決問題：**
- ✅ Cloud Run Jobs 日誌輸出（完全解決）
- ✅ 截圖上傳到 GCS（正常運作）
- ✅ 環境變數管理（Secret Manager）
- ✅ Xvfb 虛擬顯示器設定

**未解決問題：**
- ❌ reCAPTCHA v3 反機器人檢測（Phase 2-4 全部失敗）
- ❌ Headless 模式被識別
- ❌ 無法在雲端環境執行自動化

### 結論

**目前狀態：** 只有 Phase 1（本地有頭模式）能成功通過 reCAPTCHA 驗證

**技術限制：**
1. reCAPTCHA v3 使用機器學習分析用戶行為
2. Headless 瀏覽器天生缺少真實瀏覽器特徵
3. 即使使用反檢測技術和養軌跡策略，仍無法完全模擬真實用戶

**可能的解決方案：**
1. **使用真實瀏覽器**：部署到有桌面環境的 VPS（成本較高）
2. **第三方服務**：使用 2Captcha、Anti-Captcha 等服務（需付費）
3. **改變策略**：尋找其他突破點或手動半自動化流程
4. **等待網站改版**：期待未來移除 reCAPTCHA 或改用其他驗證方式

---

## 🔧 維護注意事項

### 定期檢查項目
- **網站結構變化**：台北市政府網站改版影響
- **reCAPTCHA 政策更新**：檢測機制升級
- **瀏覽器版本**：Playwright 與 Chromium 更新

### 應變策略
- **備用瀏覽路徑**：準備 2-3 套不同的養軌跡方案
- **參數調整**：根據成功率動態調整延遲時間
- **降級方案**：必要時回到手動申請

---

**版本**: v1.4 | **更新**: 2025-10-06 | **適用於**: 各 Phase 測試總結與技術限制說明

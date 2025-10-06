# 台北街頭藝人申請系統 - 設定檔

import os

# Phase 控制 (可透過環境變數 PHASE=1 或 PHASE=2 控制)
CURRENT_PHASE = int(os.getenv('PHASE', '1'))  # 預設為 Phase 1

# 網站設定
TAIPEI_ARTIST_WEBSITE_URL = "https://tpbusker.gov.taipei/signin.aspx"
APPLY_PAGE_URL = "https://tpbusker.gov.taipei/apply.aspx"

# 登入設定 (從 Repository Secrets 讀取)
TAIPEI_ARTIST_USERNAME = os.getenv('TAIPEI_USERNAME')
TAIPEI_ARTIST_PASSWORD = os.getenv('TAIPEI_PASSWORD')

# 檢查必要的環境變數
if not TAIPEI_ARTIST_USERNAME or not TAIPEI_ARTIST_PASSWORD:
    print("⚠️  警告：未設定 TAIPEI_USERNAME 或 TAIPEI_PASSWORD 環境變數")
    print("   本機測試請設定環境變數，GitHub Actions 請檢查 Repository Secrets")

# 場地申請網址配置 (直接進入各場地的日曆頁面)
VENUE_URLS = {
    "大安森林公園_2號門": "https://tpbusker.gov.taipei/apply.aspx?pl=9&loc=67",
    "北投公園_1號點": "https://tpbusker.gov.taipei/applys3.aspx?pl=4&loc=287"
}

# 當前使用的場地 (可在此切換不同場地進行測試)
CURRENT_VENUE_URL = VENUE_URLS["北投公園_1號點"]  # 目前使用北投公園測試

# 表演項目設定 (填入「本次展演項目」欄位)
PERFORMANCE_ITEMS = "唱歌、跳舞、助盲"

# 重試設定
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 30

# GitHub Actions 執行時間限制 (建議 10 分鐘)
EXECUTION_TIMEOUT_MINUTES = 10

# 網站結構分析輸出檔案
WEBSITE_STRUCTURE_FILE = "website_structure.json"

# 反檢測設定
ANTI_DETECTION_ENABLED = True

# 截圖設定
SCREENSHOT_DIR = "screenshots"

# 養軌跡設定
TRAJECTORY_BUILDING_ENABLED = True
TRAJECTORY_SITES = [
    {
        "url": "https://www.google.com/",
        "name": "Google 首頁",
        "stay_time": (10, 15),
        "actions": ["scroll"]
    },
    {
        "url": "https://www.gov.taipei/",
        "name": "台北市政府首頁",
        "stay_time": (15, 25),
        "actions": ["scroll"]
    },
    {
        "url": "https://service.taipei/",
        "name": "市民服務專區", 
        "stay_time": (20, 30),
        "actions": ["scroll", "hover_links"]
    },
    {
        "url": "https://culture.gov.taipei/",
        "name": "文化局網站",
        "stay_time": (15, 20),
        "actions": ["scroll"]
    }
]

# 人類行為模擬設定 (根據 Phase 調整)
HUMAN_BEHAVIOR_SIMULATION = {
    "typing_delay_range": (80, 200) if CURRENT_PHASE >= 2 else (50, 150),  # Phase 2+ 增加打字間隔
    "click_delay_range": (150, 400) if CURRENT_PHASE >= 2 else (100, 300),  # Phase 2+ 增加點擊延遲
    "operation_delay_range": (1500, 4000) if CURRENT_PHASE >= 2 else (1000, 3000),  # Phase 2+ 增加操作間隔
    "mouse_offset_range": (-8, 8) if CURRENT_PHASE >= 2 else (-5, 5)  # Phase 2+ 增加滑鼠隨機性
}

# 瀏覽器設定 (根據 Phase 自動調整)
BROWSER_CONFIG = {
    "headless": CURRENT_PHASE >= 2,  # Phase 1: False (有畫面), Phase 2+: True (無畫面)
    "viewport": {"width": 1366, "height": 768},
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" if CURRENT_PHASE >= 2 else "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 增強 headless 反檢測參數
HEADLESS_STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage", 
    "--disable-web-security",
    "--disable-features=VizDisplayCompositor",
    "--no-first-run",
    "--disable-extensions-file-access-check",
    "--disable-default-apps",
    "--disable-component-extensions-with-background-pages",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-field-trial-config"
]

# Google Cloud Storage 設定（Phase 4 使用）
GCS_CONFIG = {
    "bucket_name": "street-artist-screenshots",
    "project_id": "street-artist-automation-tp",
    "location": "asia-east1",
}

# Phase 相關設定
PHASE_CONFIG = {
    1: {
        "name": "有畫面除錯",
        "description": "觀察每個步驟，確認流程正確",
        "log_level": "INFO"
    },
    2: {
        "name": "無畫面測試", 
        "description": "模擬 GitHub Actions 環境",
        "log_level": "DEBUG"
    },
    3: {
        "name": "GitHub Actions + xvfb",
        "description": "雲端執行 + 虛擬顯示器",
        "log_level": "DEBUG"
    },
    4: {
        "name": "Cloud Run + GCS",
        "description": "雲端執行 + 截圖上傳 GCS",
        "log_level": "DEBUG"
    }
}

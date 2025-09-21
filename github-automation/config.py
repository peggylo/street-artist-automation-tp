# 台北街頭藝人申請系統 - 設定檔

# 網站設定
TAIPEI_ARTIST_WEBSITE_URL = "https://tpbusker.gov.taipei/signin.aspx"
APPLY_PAGE_URL = "https://tpbusker.gov.taipei/apply.aspx"

# 場地設定
DEFAULT_VENUE = "大安森林公園"
DEFAULT_EXIT = "2號門入口"  # 可調整的出口選項

# 表演項目設定 (填入「本次展演項目」欄位)
PERFORMANCE_ITEMS = "唱歌、跳舞、助盲"

# 重試設定
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 30

# GitHub Actions 執行時間限制 (建議 10 分鐘)
EXECUTION_TIMEOUT_MINUTES = 10

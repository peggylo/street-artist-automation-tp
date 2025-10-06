# 台北街頭藝人申請系統 - Cloud Run Dockerfile
# 使用 Python 3.11 官方 image
FROM python:3.11

# 設定工作目錄
WORKDIR /app

# 安裝系統相依套件
RUN apt-get update && apt-get install -y \
    # xvfb 虛擬顯示器
    xvfb \
    # Chromium 瀏覽器相依套件
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY github-automation/requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 安裝 Playwright Chromium
RUN playwright install chromium

# 手動安裝 Playwright 依賴（避免 Debian 13 套件名稱問題）
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 複製程式碼
COPY github-automation/ /app/

# 建立截圖目錄
RUN mkdir -p /app/screenshots

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PHASE=4
ENV PYTHONDONTWRITEBYTECODE=1

# 複製啟動腳本
COPY cloud-run/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 啟動指令：使用診斷版啟動腳本
CMD ["/app/entrypoint.sh"]


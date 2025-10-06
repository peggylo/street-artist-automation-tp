#!/bin/bash
# Cloud Run 啟動腳本 - 診斷版本

# 確保輸出立即顯示
set -e
exec 1>&1  # 確保 stdout 正確轉發
exec 2>&2  # 確保 stderr 正確轉發

echo "=========================================="
echo "🚀 Container 啟動中..."
echo "=========================================="
echo "時間: $(date)"
echo "主機名稱: $(hostname)"
echo "Python 版本: $(python --version)"
echo "工作目錄: $(pwd)"
echo ""

echo "📋 環境變數檢查:"
echo "PHASE=${PHASE:-未設定}"
echo "PYTHONUNBUFFERED=${PYTHONUNBUFFERED:-未設定}"
echo "TAIPEI_USERNAME=$([ -n "$TAIPEI_USERNAME" ] && echo "已設定(${#TAIPEI_USERNAME} 字元)" || echo "未設定")"
echo "TAIPEI_PASSWORD=$([ -n "$TAIPEI_PASSWORD" ] && echo "已設定" || echo "未設定")"
echo ""

echo "📦 Python 套件檢查:"
python -c "from playwright.sync_api import sync_playwright; print('✅ playwright 已安裝')" 2>&1 || echo "❌ playwright 載入失敗"
python -c "from google.cloud import storage; print('✅ google-cloud-storage 已安裝')" 2>&1 || echo "❌ google-cloud-storage 載入失敗"
echo ""

echo "🖥️  顯示器設定:"
echo "DISPLAY=${DISPLAY:-未設定}"
echo ""

echo "📁 檔案檢查:"
ls -lh /app/*.py 2>&1 | head -5
echo ""

echo "=========================================="
echo "🎬 啟動主程式..."
echo "=========================================="
echo ""

# 先啟動 xvfb 在背景
Xvfb :99 -screen 0 1366x768x24 >/dev/null 2>&1 &
XVFB_PID=$!
export DISPLAY=:99

# 等待 xvfb 啟動
sleep 2
echo "✅ Xvfb 已在背景啟動 (DISPLAY=:99, PID=$XVFB_PID)"
echo ""

# 直接執行 Python，不透過 xvfb-run
exec python -u main.py


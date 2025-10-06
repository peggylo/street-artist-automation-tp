#!/bin/bash

# 台北街頭藝人申請系統 - Cloud Run 部署腳本
# 使用方式：./cloud-run/deploy.sh

set -e  # 遇到錯誤立即停止

# ===== 配置參數 =====
PROJECT_ID="street-artist-automation-tp"
REGION="asia-east1"
REPOSITORY="street-artist-images"
IMAGE_NAME="street-artist-app"
JOB_NAME="street-artist-job"

# 完整 image 路徑
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}"

# ===== 顏色輸出 =====
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  台北街頭藝人申請系統 - Cloud Run 部署${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ===== 步驟 1：檢查必要工具 =====
echo -e "${YELLOW}[1/4] 檢查必要工具...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ 錯誤：未安裝 gcloud CLI${NC}"
    echo "請參考：https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo -e "${GREEN}✅ 工具檢查完成（不需要 Docker）${NC}"
echo ""

# ===== 步驟 2：驗證 GCP 認證 =====
echo -e "${YELLOW}[2/4] 驗證 GCP 認證...${NC}"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  當前專案：$CURRENT_PROJECT${NC}"
    echo -e "${YELLOW}⚠️  切換到：$PROJECT_ID${NC}"
    gcloud config set project $PROJECT_ID
fi
echo -e "${GREEN}✅ 認證完成 - 專案：$PROJECT_ID${NC}"
echo ""

# ===== 步驟 3：部署到 Cloud Run（自動建置）=====
echo -e "${YELLOW}[3/4] 部署到 Cloud Run（Cloud Build 自動建置）...${NC}"
echo -e "${BLUE}ℹ️  使用 Dockerfile: cloud-run/Dockerfile${NC}"
echo -e "${BLUE}ℹ️  Image 將推送到: $IMAGE_URL${NC}"
echo ""

gcloud builds submit --config cloud-run/cloudbuild.yaml .

echo ""
echo -e "${GREEN}✅ Image 建置並推送完成${NC}"
echo ""

# 部署到 Cloud Run Jobs
gcloud run jobs deploy $JOB_NAME \
    --image $IMAGE_URL:latest \
    --region $REGION \
    --memory 2Gi \
    --cpu 1 \
    --task-timeout 900 \
    --max-retries 0 \
    --set-env-vars PHASE=4 \
    --set-secrets TAIPEI_USERNAME=TAIPEI_USERNAME:latest,TAIPEI_PASSWORD=TAIPEI_PASSWORD:latest \
    --service-account street-artist-tp-runner@${PROJECT_ID}.iam.gserviceaccount.com

echo -e "${GREEN}✅ Cloud Run Job 部署完成${NC}"
echo -e "${BLUE}ℹ️  執行指令：gcloud run jobs execute $JOB_NAME --region $REGION${NC}"
echo ""

# ===== 步驟 4：清理舊版本 Image =====
echo -e "${YELLOW}[4/4] 清理舊版本 Image...${NC}"

# 列出所有 digest（排除 latest tag）
DIGESTS=$(gcloud artifacts docker images list \
    $IMAGE_URL \
    --format="get(digest)" \
    --sort-by="~CREATE_TIME" \
    --limit=999 2>/dev/null || echo "")

if [ -z "$DIGESTS" ]; then
    echo -e "${BLUE}ℹ️  沒有需要清理的舊版本${NC}"
else
    # 計算數量
    TOTAL_COUNT=$(echo "$DIGESTS" | wc -l)
    
    if [ $TOTAL_COUNT -le 2 ]; then
        echo -e "${BLUE}ℹ️  目前有 $TOTAL_COUNT 個版本，不需要清理${NC}"
    else
        # 保留最近 2 個，刪除其他
        KEEP_COUNT=2
        DELETE_COUNT=$((TOTAL_COUNT - KEEP_COUNT))
        
        echo -e "${YELLOW}⚠️  發現 $TOTAL_COUNT 個版本，將刪除最舊的 $DELETE_COUNT 個${NC}"
        
        # 跳過前 2 個，刪除其他
        echo "$DIGESTS" | tail -n +3 | while read digest; do
            echo "刪除: $digest"
            gcloud artifacts docker images delete \
                "${IMAGE_URL}@${digest}" \
                --quiet \
                --delete-tags 2>/dev/null || echo "  (已刪除或不存在)"
        done
        
        echo -e "${GREEN}✅ 清理完成，保留最近 $KEEP_COUNT 個版本${NC}"
    fi
fi
echo ""

# ===== 完成 =====
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🎉 部署流程全部完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "服務資訊："
echo "  服務名稱：$SERVICE_NAME"
echo "  地區：$REGION"
echo "  Image：$IMAGE_URL:latest"
echo ""
echo "查看服務狀態："
echo "  gcloud run services describe $SERVICE_NAME --region $REGION"
echo ""
echo "查看日誌："
echo "  gcloud run logs read $SERVICE_NAME --region $REGION --limit 50"
echo ""
echo "觸發執行："
echo "  SERVICE_URL=\$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')"
echo "  curl \$SERVICE_URL"
echo ""


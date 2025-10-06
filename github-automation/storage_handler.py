"""
截圖儲存處理模組
負責處理不同環境下的截圖儲存邏輯
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)

# 確保日誌輸出
print("📦 storage_handler 模組初始化中...", flush=True)
sys.stdout.flush()


class ScreenshotStorageHandler:
    """截圖儲存處理器"""
    
    def __init__(self, phase: int, gcs_config: dict = None):
        """
        初始化截圖儲存處理器
        
        Args:
            phase: 當前執行的 Phase (1-4)
            gcs_config: GCS 配置（Phase 4 需要）
        """
        self.phase = phase
        self.gcs_config = gcs_config
        self.screenshots_dir = Path("screenshots")
        
        # Phase 4 需要 GCS 客戶端
        if self.phase == 4:
            if not gcs_config:
                raise ValueError("Phase 4 需要提供 gcs_config")
            self._init_gcs_client()
    
    def _init_gcs_client(self):
        """初始化 Google Cloud Storage 客戶端"""
        try:
            print(f"📦 載入 google.cloud.storage 模組...", flush=True)
            from google.cloud import storage
            print(f"✅ google.cloud.storage 模組載入成功", flush=True)
            
            # Cloud Run 環境會自動使用 Service Account 認證
            print(f"🔐 初始化 GCS 客戶端 (專案: {self.gcs_config['project_id']})...", flush=True)
            self.gcs_client = storage.Client(project=self.gcs_config["project_id"])
            self.bucket = self.gcs_client.bucket(self.gcs_config["bucket_name"])
            
            logger.info(f"✅ GCS 客戶端初始化成功")
            logger.info(f"   專案: {self.gcs_config['project_id']}")
            logger.info(f"   Bucket: {self.gcs_config['bucket_name']}")
            print(f"✅ GCS 客戶端初始化成功 (Bucket: {self.gcs_config['bucket_name']})", flush=True)
            
        except Exception as e:
            error_msg = f"❌ GCS 客戶端初始化失敗: {e}"
            logger.error(error_msg)
            print(error_msg, flush=True)
            import traceback
            traceback.print_exc()
            raise
    
    def get_screenshot_files(self) -> List[Path]:
        """
        取得所有截圖檔案
        
        Returns:
            截圖檔案路徑列表
        """
        if not self.screenshots_dir.exists():
            logger.warning(f"⚠️  截圖目錄不存在: {self.screenshots_dir}")
            return []
        
        # 支援常見圖片格式
        extensions = ['*.png', '*.jpg', '*.jpeg']
        screenshot_files = []
        
        for ext in extensions:
            screenshot_files.extend(self.screenshots_dir.glob(ext))
        
        screenshot_files.sort(key=lambda x: x.stat().st_mtime)
        
        logger.info(f"📸 找到 {len(screenshot_files)} 個截圖檔案")
        return screenshot_files
    
    def upload_to_gcs(self) -> Optional[List[str]]:
        """
        上傳截圖到 Google Cloud Storage
        
        Returns:
            上傳成功的 GCS URLs，失敗返回 None
        """
        if self.phase != 4:
            logger.debug("非 Phase 4，跳過 GCS 上傳")
            return None
        
        screenshot_files = self.get_screenshot_files()
        
        if not screenshot_files:
            logger.warning("⚠️  沒有截圖需要上傳")
            return []
        
        logger.info(f"🚀 開始上傳 {len(screenshot_files)} 個截圖到 GCS...")
        
        uploaded_urls = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            for screenshot_file in screenshot_files:
                # GCS 路徑：screenshots/YYYYMMDD_HHMMSS/filename.png
                blob_name = f"screenshots/{timestamp}/{screenshot_file.name}"
                blob = self.bucket.blob(blob_name)
                
                # 上傳檔案
                blob.upload_from_filename(str(screenshot_file))
                
                # 取得公開 URL（如果 bucket 是公開的）
                # 或使用 gs:// 格式的 URL
                gcs_url = f"gs://{self.gcs_config['bucket_name']}/{blob_name}"
                uploaded_urls.append(gcs_url)
                
                logger.info(f"   ✅ {screenshot_file.name} → {gcs_url}")
            
            logger.info(f"🎉 所有截圖上傳完成！")
            logger.info(f"   查看截圖：https://console.cloud.google.com/storage/browser/{self.gcs_config['bucket_name']}/screenshots/{timestamp}")
            
            return uploaded_urls
            
        except Exception as e:
            logger.error(f"❌ 上傳截圖到 GCS 失敗: {e}")
            return None
    
    def cleanup_local_screenshots(self, keep_files: bool = False):
        """
        清理本機截圖檔案
        
        Args:
            keep_files: 是否保留檔案（預設 False，Phase 4 會刪除以節省空間）
        """
        if keep_files:
            logger.debug("保留本機截圖檔案")
            return
        
        # Phase 4 且上傳成功後，刪除本機檔案以節省容器空間
        if self.phase == 4:
            screenshot_files = self.get_screenshot_files()
            
            if not screenshot_files:
                return
            
            logger.info("🧹 清理本機截圖檔案...")
            
            for screenshot_file in screenshot_files:
                try:
                    screenshot_file.unlink()
                    logger.debug(f"   刪除: {screenshot_file.name}")
                except Exception as e:
                    logger.warning(f"   無法刪除 {screenshot_file.name}: {e}")
            
            logger.info("✅ 本機截圖清理完成")
    
    def process_screenshots(self) -> dict:
        """
        根據 Phase 處理截圖
        
        Returns:
            處理結果字典
        """
        result = {
            "phase": self.phase,
            "screenshot_count": 0,
            "storage_location": "",
            "gcs_urls": [],
            "success": False
        }
        
        screenshot_files = self.get_screenshot_files()
        result["screenshot_count"] = len(screenshot_files)
        
        if not screenshot_files:
            logger.warning("⚠️  沒有找到任何截圖")
            return result
        
        # Phase 1, 2: 本機資料夾
        if self.phase in [1, 2]:
            result["storage_location"] = f"本機資料夾: {self.screenshots_dir.absolute()}"
            result["success"] = True
            logger.info(f"📁 截圖儲存於: {result['storage_location']}")
        
        # Phase 3: GitHub Actions Artifacts（程式不處理，由 workflow 處理）
        elif self.phase == 3:
            result["storage_location"] = f"本機資料夾（GitHub Actions 會自動打包成 Artifacts）"
            result["success"] = True
            logger.info(f"📁 截圖儲存於: {result['storage_location']}")
        
        # Phase 4: Google Cloud Storage
        elif self.phase == 4:
            gcs_urls = self.upload_to_gcs()
            
            if gcs_urls:
                result["gcs_urls"] = gcs_urls
                result["storage_location"] = f"Google Cloud Storage: {self.gcs_config['bucket_name']}"
                result["success"] = True
                
                # 上傳成功後清理本機檔案
                self.cleanup_local_screenshots(keep_files=False)
            else:
                logger.error("❌ 截圖上傳 GCS 失敗")
        
        return result


def handle_screenshots(phase: int, gcs_config: dict = None) -> dict:
    """
    便捷函數：處理截圖儲存
    
    Args:
        phase: 當前執行的 Phase (1-4)
        gcs_config: GCS 配置（Phase 4 需要）
    
    Returns:
        處理結果字典
    """
    handler = ScreenshotStorageHandler(phase, gcs_config)
    return handler.process_screenshots()


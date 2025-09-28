#!/usr/bin/env python3
"""
台北街頭藝人申請系統 - 主程式

整合反檢測技術的街頭藝人申請自動化系統
"""

import asyncio
import json
import os
import logging
from pathlib import Path
from datetime import datetime
from anti_detection import AntiDetectionManager, LoginAntiDetection
from config import (
    TAIPEI_ARTIST_USERNAME,
    TAIPEI_ARTIST_PASSWORD,
    CURRENT_VENUE_URL,
    PERFORMANCE_ITEMS,
    ANTI_DETECTION_ENABLED,
    BROWSER_CONFIG,
    SCREENSHOT_DIR,
    TRAJECTORY_BUILDING_ENABLED,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
    CURRENT_PHASE,
    PHASE_CONFIG
)

# 設定日誌系統
def setup_logging():
    """設定日誌系統"""
    phase_info = PHASE_CONFIG.get(CURRENT_PHASE, PHASE_CONFIG[1])
    log_level = getattr(logging, phase_info["log_level"], logging.INFO)
    
    # 設定日誌格式
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 設定根日誌器
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.handlers.clear()  # 清除現有處理器
    logger.addHandler(console_handler)
    
    return logger

# 初始化日誌
logger = setup_logging()


class StreetArtistApplication:
    """街頭藝人申請主程式"""
    
    def __init__(self):
        self.anti_detection = None
        self.page = None
        self.applied_slots = []
        self.screenshot_dir = Path(SCREENSHOT_DIR)
        
        # 確保截圖目錄存在
        self.screenshot_dir.mkdir(exist_ok=True)
        
    async def initialize_browser(self):
        """初始化反檢測瀏覽器"""
        phase_info = PHASE_CONFIG[CURRENT_PHASE]
        logger.info("🚀 初始化反檢測瀏覽器系統...")
        logger.info(f"📋 當前執行模式: Phase {CURRENT_PHASE} - {phase_info['name']}")
        logger.info(f"📝 模式描述: {phase_info['description']}")
        logger.info(f"🖥️  Headless 模式: {BROWSER_CONFIG['headless']}")
        
        if ANTI_DETECTION_ENABLED:
            logger.debug("🔧 啟動反檢測管理器...")
            self.anti_detection = AntiDetectionManager(
                headless=BROWSER_CONFIG["headless"],
                screenshot_dir=SCREENSHOT_DIR
            )
            self.page = await self.anti_detection.start_browser()
            logger.debug("✅ 反檢測瀏覽器啟動完成")
        else:
            logger.warning("⚠️  反檢測功能已停用，使用基本瀏覽器")
            # 這裡可以加入基本瀏覽器啟動邏輯
            
        logger.info("✅ 瀏覽器系統初始化完成")
    
    async def build_browsing_trajectory(self):
        """建立瀏覽軌跡"""
        if TRAJECTORY_BUILDING_ENABLED and self.anti_detection:
            logger.info("🎪 開始建立瀏覽軌跡以規避機器人檢測...")
            logger.debug("📍 執行軌跡建立以提升登入成功率...")
            await self.anti_detection.perform_trajectory_building()
            logger.info("✅ 瀏覽軌跡建立完成")
        else:
            logger.warning("⚠️  跳過軌跡建立階段")
    
    async def perform_login(self):
        """執行登入流程"""
        logger.info("🔐 開始執行登入流程...")
        if TAIPEI_ARTIST_USERNAME:
            logger.debug(f"👤 使用帳號: {TAIPEI_ARTIST_USERNAME[:4]}****")
        else:
            logger.error("❌ 未設定 TAIPEI_USERNAME 環境變數")
        
        if ANTI_DETECTION_ENABLED and self.anti_detection:
            logger.debug("🛡️  使用增強版反檢測登入...")
            # 使用增強版登入
            login_handler = LoginAntiDetection(self.anti_detection)
            success = await login_handler.perform_enhanced_login(
                TAIPEI_ARTIST_USERNAME, 
                TAIPEI_ARTIST_PASSWORD
            )
            
            if success:
                logger.info("✅ 增強版登入成功！")
                return True
            else:
                logger.error("❌ 增強版登入失敗")
                return False
        else:
            # 使用基本登入（原有邏輯）
            logger.warning("⚠️  使用基本登入流程")
            return await self.basic_login()
    
    async def basic_login(self):
        """基本登入流程（原有邏輯的簡化版）"""
        # 這裡保留原有的基本登入邏輯作為備用
        logger.info("🔐 執行基本登入流程...")
        logger.debug("⚠️  基本登入功能尚未實作")
        # 實作基本登入...
        return False  # 暫時返回 False
    
    async def navigate_to_venue(self):
        """導航到指定場地時段頁面"""
        logger.info("🏢 前往場地時段頁面...")
        
        try:
            # 使用配置檔案中的場地網址
            logger.info(f"📍 前往時段頁面: {CURRENT_VENUE_URL}")
            logger.debug("🌐 載入頁面中...")
            await self.page.goto(CURRENT_VENUE_URL, wait_until='networkidle')
            
            # 使用反檢測等待
            if self.anti_detection:
                logger.debug("⏱️  執行反檢測延遲...")
                await self.anti_detection.wait_with_random_delay(2000, 4000)
                await self.anti_detection.take_screenshot("venue_page")
                logger.debug("📸 場地頁面截圖完成")
            else:
                await self.page.wait_for_timeout(3000)
            
            logger.info("✅ 成功進入時段頁面")
            return True
            
        except Exception as e:
            logger.error(f"❌ 導航到時段頁面失敗: {e}")
            return False
    
    async def apply_time_slots(self):
        """申請所有可用時段（動態搜尋方式）"""
        logger.info("⏰ 開始申請可用時段...")
        logger.debug("🔍 使用動態搜尋方式尋找可申請時段...")
        
        try:
            # 尋找「個人登記」按鈕的選擇器
            personal_register_selectors = [
                '.button_apply[title="個人登記"]',
                'text="個人登記"',
                'button:has-text("個人登記")',
                '[title="個人登記"]'
            ]
            
            # 使用動態搜尋方式，直到沒有「個人登記」按鈕為止
            max_attempts = 20  # 最多申請 20 個時段，避免無限迴圈
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                
                try:
                    logger.info(f"📝 搜尋第 {attempt} 個可申請時段...")
                    
                    # 重新搜尋所有「個人登記」按鈕
                    current_buttons = []
                    for selector in personal_register_selectors:
                        try:
                            buttons = await self.page.query_selector_all(selector)
                            if buttons:
                                current_buttons = buttons
                                logger.debug(f"✅ 使用選擇器 '{selector}' 找到 {len(buttons)} 個按鈕")
                                break
                        except:
                            continue
                    
                    # 如果沒有找到任何「個人登記」按鈕，表示全部申請完成
                    if not current_buttons:
                        logger.info(f"✅ 沒有更多可申請時段，共申請了 {len(self.applied_slots)} 個時段")
                        break
                    
                    logger.info(f"🔍 找到 {len(current_buttons)} 個剩餘時段，申請第一個...")
                    logger.debug("🎯 準備點擊第一個「個人登記」按鈕...")
                    
                    # 總是點擊第一個找到的「個人登記」按鈕
                    target_button = current_buttons[0]
                    
                    # 使用反檢測點擊
                    if self.anti_detection:
                        # 先截圖當前狀態
                        await self.anti_detection.take_screenshot(f"before_slot_{attempt}")
                        
                        # 點擊第一個個人登記按鈕
                        await target_button.click()
                        await self.page.wait_for_load_state('networkidle')
                        await self.anti_detection.wait_with_random_delay(2000, 4000)
                        
                        # 截圖申請表單
                        await self.anti_detection.take_screenshot(f"form_slot_{attempt}")
                        
                        # 填寫表演項目
                        performance_selectors = [
                            'textarea',
                            'textarea[name*="項目"]',
                            'input[name*="項目"]'
                        ]
                        
                        performance_filled = False
                        for perf_selector in performance_selectors:
                            if await self.anti_detection.human_like_type(
                                perf_selector, PERFORMANCE_ITEMS, "表演項目"
                            ):
                                performance_filled = True
                                break
                        
                        if not performance_filled:
                            logger.warning("⚠️  無法填寫表演項目")
                        else:
                            logger.debug(f"✅ 表演項目填寫完成: {PERFORMANCE_ITEMS}")
                        
                        # 等待一下再送出
                        logger.debug("⏱️  等待後準備送出申請...")
                        await self.anti_detection.wait_with_random_delay(1000, 2000)
                        
                        # 點擊確定送出
                        submit_selectors = [
                            'button:has-text("確定送出")',
                            'input[value="確定送出"]',
                            'button:has-text("送出")',
                            'input[type="submit"]'
                        ]
                        
                        submit_success = False
                        for submit_selector in submit_selectors:
                            if await self.anti_detection.human_like_click(
                                submit_selector, "送出按鈕"
                            ):
                                submit_success = True
                                break
                        
                        if submit_success:
                            # 等待成功彈跳視窗
                            try:
                                success_popup = await self.page.wait_for_selector(
                                    'text="個人登記(需管理者審核通過)完成!"', 
                                    timeout=10000
                                )
                                if success_popup:
                                    logger.info("🎉 申請成功！")
                                    
                                    # 截圖成功彈跳視窗
                                    await self.anti_detection.take_screenshot(f"success_slot_{attempt}")
                                    logger.debug("📸 成功彈跳視窗截圖完成")
                                    
                                    # 點擊確定
                                    confirm_btn = await self.page.wait_for_selector(
                                        'button:has-text("確定")', 
                                        timeout=5000
                                    )
                                    if confirm_btn:
                                        logger.debug("🔘 點擊確認按鈕...")
                                        await self.anti_detection.human_like_click(
                                            'button:has-text("確定")', "確認按鈕"
                                        )
                                        
                                        # 重要：等待 5 秒讓頁面跳回日曆頁面
                                        logger.debug("⏱️  等待 5 秒讓頁面跳回日曆...")
                                        await self.anti_detection.wait_with_random_delay(5000, 6000)
                                        
                                        self.applied_slots.append(f"時段 {attempt}")
                                        logger.info(f"🎉 第 {attempt} 個時段申請成功！")
                                
                            except Exception as popup_error:
                                logger.warning(f"⚠️  處理成功彈跳視窗時發生錯誤: {popup_error}")
                        else:
                            logger.error("❌ 無法點擊送出按鈕")
                    
                    # 每次申請完成後都確保回到日曆頁面（無論成功或失敗）
                    logger.debug("🔄 確認回到時段選擇頁面...")
                    current_url = self.page.url
                    logger.debug(f"🌐 當前頁面: {current_url}")
                    if CURRENT_VENUE_URL not in current_url:
                        # 如果不在日曆頁面，重新導航
                        logger.debug("🔄 重新導航回日曆頁面...")
                        await self.page.goto(CURRENT_VENUE_URL)
                        await self.page.wait_for_load_state('networkidle')
                    
                    if self.anti_detection:
                        await self.anti_detection.wait_with_random_delay(2000, 3000)
                    
                except Exception as slot_error:
                    logger.error(f"❌ 申請第 {attempt} 個時段時發生錯誤: {slot_error}")
                    # 發生錯誤時也要確保回到日曆頁面
                    try:
                        logger.debug("🔄 錯誤恢復：重新導航回日曆頁面...")
                        await self.page.goto(CURRENT_VENUE_URL)
                        await self.page.wait_for_load_state('networkidle')
                        if self.anti_detection:
                            await self.anti_detection.wait_with_random_delay(2000, 3000)
                    except:
                        pass
                    continue
            
            # 檢查是否達到最大嘗試次數
            if attempt >= max_attempts:
                logger.warning(f"⚠️  達到最大嘗試次數 ({max_attempts})，停止申請")
            
            logger.info(f"✅ 時段申請完成，成功申請: {len(self.applied_slots)} 個時段")
            return True
            
        except Exception as e:
            logger.error(f"❌ 申請時段時發生錯誤: {e}")
            return False
    
    async def take_final_screenshot(self):
        """拍攝最終截圖"""
        logger.info("📸 拍攝最終截圖...")
        
        try:
            if self.anti_detection:
                await self.anti_detection.take_screenshot("final_result", full_page=True)
                logger.info("✅ 最終截圖已儲存 (透過反檢測管理器)")
            else:
                screenshot_path = self.screenshot_dir / "final_result.png"
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                logger.info(f"✅ 最終截圖已儲存: {screenshot_path}")
        except Exception as e:
            logger.warning(f"⚠️  最終截圖失敗: {e}")
    
    async def cleanup(self):
        """清理資源"""
        logger.debug("🧹 開始清理瀏覽器資源...")
        if self.anti_detection:
            await self.anti_detection.close_browser()
            logger.debug("✅ 反檢測瀏覽器清理完成")
        else:
            logger.info("✅ 基本清理完成")
    
    async def run_with_retry(self):
        """帶重試機制的主執行流程"""
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"\n🎯 開始第 {attempt} 次嘗試...")
            logger.info("=" * 60)
            
            try:
                success = await self.run_single_attempt()
                if success:
                    logger.info(f"✅ 第 {attempt} 次嘗試成功！")
                    return True
                else:
                    logger.error(f"❌ 第 {attempt} 次嘗試失敗")
                    
            except Exception as e:
                logger.error(f"❌ 第 {attempt} 次嘗試發生異常: {e}")
            
            # 清理當前嘗試的資源
            await self.cleanup()
            
            # 如果不是最後一次嘗試，等待後重試
            if attempt < MAX_RETRIES:
                logger.info(f"⏱️  等待 {RETRY_DELAY_SECONDS} 秒後重試...")
                await asyncio.sleep(RETRY_DELAY_SECONDS)
        
        logger.error(f"❌ 所有 {MAX_RETRIES} 次嘗試都失敗了")
        return False
    
    async def run_single_attempt(self):
        """單次完整執行流程"""
        try:
            # 初始化瀏覽器
            await self.initialize_browser()
            
            # 建立瀏覽軌跡
            await self.build_browsing_trajectory()
            
            # 執行登入
            login_success = await self.perform_login()
            if not login_success:
                logger.error("❌ 登入失敗，終止此次嘗試")
                return False
            
            # 導航到場地頁面
            nav_success = await self.navigate_to_venue()
            if not nav_success:
                logger.error("❌ 導航失敗，終止此次嘗試")
                return False
            
            # 申請時段
            apply_success = await self.apply_time_slots()
            if not apply_success:
                logger.error("❌ 申請時段失敗")
                return False
            
            # 拍攝最終截圖
            await self.take_final_screenshot()
            
            # 顯示結果摘要
            self.show_results()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 執行過程發生錯誤: {e}")
            return False
    
    def show_results(self):
        """顯示申請結果摘要"""
        logger.info("\n" + "="*60)
        logger.info("🎯 申請結果摘要:")
        logger.info(f"✅ 成功申請時段數: {len(self.applied_slots)}")
        if self.applied_slots:
            for slot in self.applied_slots:
                logger.info(f"   - {slot}")
        else:
            logger.warning("   - 無可申請時段或申請失敗")
        logger.info(f"📁 截圖位置: {self.screenshot_dir}")
        logger.info("="*60)


async def main():
    """主函數"""
    phase_info = PHASE_CONFIG.get(CURRENT_PHASE, PHASE_CONFIG[1])
    logger.info("🎯 台北街頭藝人申請系統 (反檢測增強版)")
    logger.info("=" * 60)
    logger.info(f"🚀 啟動模式: Phase {CURRENT_PHASE} - {phase_info['name']}")
    logger.info(f"📝 模式描述: {phase_info['description']}")
    logger.info(f"📋 執行環境: Headless={BROWSER_CONFIG['headless']}")
    
    # 檢查環境變數
    if not TAIPEI_ARTIST_USERNAME or not TAIPEI_ARTIST_PASSWORD:
        logger.error("❌ 缺少必要的環境變數 TAIPEI_USERNAME 或 TAIPEI_PASSWORD")
        logger.error("   請檢查 Repository Secrets 設定或本機環境變數")
        return
    
    # 顯示 Phase 3 特殊資訊
    if CURRENT_PHASE == 3:
        logger.info("🌐 GitHub Actions 執行環境")
        logger.info("🖥️  使用 xvfb 虛擬顯示器")
        logger.info("📸 截圖將上傳到 Artifacts")
    
    app = StreetArtistApplication()
    
    try:
        success = await app.run_with_retry()
        if success:
            logger.info("\n🎉 程式執行成功！")
        else:
            logger.error("\n😞 程式執行失敗，請檢查錯誤訊息")
    
    finally:
        # 確保資源清理
        await app.cleanup()
        logger.info("🧹 資源清理完成")


if __name__ == "__main__":
    asyncio.run(main())
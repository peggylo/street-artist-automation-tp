#!/usr/bin/env python3
"""
台北街頭藝人申請系統 - 主程式

整合反檢測技術的街頭藝人申請自動化系統
"""

import asyncio
import json
import os
from pathlib import Path
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
    RETRY_DELAY_SECONDS
)


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
        print("🚀 初始化反檢測瀏覽器系統...")
        
        if ANTI_DETECTION_ENABLED:
            self.anti_detection = AntiDetectionManager(
                headless=BROWSER_CONFIG["headless"],
                screenshot_dir=SCREENSHOT_DIR
            )
            self.page = await self.anti_detection.start_browser()
        else:
            print("⚠️  反檢測功能已停用，使用基本瀏覽器")
            # 這裡可以加入基本瀏覽器啟動邏輯
            
        print("✅ 瀏覽器系統初始化完成")
    
    async def build_browsing_trajectory(self):
        """建立瀏覽軌跡"""
        if TRAJECTORY_BUILDING_ENABLED and self.anti_detection:
            print("🎪 開始建立瀏覽軌跡以規避機器人檢測...")
            await self.anti_detection.perform_trajectory_building()
            print("✅ 瀏覽軌跡建立完成")
        else:
            print("⚠️  跳過軌跡建立階段")
    
    async def perform_login(self):
        """執行登入流程"""
        print("🔐 開始執行登入流程...")
        
        if ANTI_DETECTION_ENABLED and self.anti_detection:
            # 使用增強版登入
            login_handler = LoginAntiDetection(self.anti_detection)
            success = await login_handler.perform_enhanced_login(
                TAIPEI_ARTIST_USERNAME, 
                TAIPEI_ARTIST_PASSWORD
            )
            
            if success:
                print("✅ 增強版登入成功！")
                return True
            else:
                print("❌ 增強版登入失敗")
                return False
        else:
            # 使用基本登入（原有邏輯）
            print("⚠️  使用基本登入流程")
            return await self.basic_login()
    
    async def basic_login(self):
        """基本登入流程（原有邏輯的簡化版）"""
        # 這裡保留原有的基本登入邏輯作為備用
        print("🔐 執行基本登入流程...")
        # 實作基本登入...
        return False  # 暫時返回 False
    
    async def navigate_to_venue(self):
        """導航到指定場地時段頁面"""
        print("🏢 前往場地時段頁面...")
        
        try:
            # 使用配置檔案中的場地網址
            print(f"📍 前往時段頁面: {CURRENT_VENUE_URL}")
            await self.page.goto(CURRENT_VENUE_URL, wait_until='networkidle')
            
            # 使用反檢測等待
            if self.anti_detection:
                await self.anti_detection.wait_with_random_delay(2000, 4000)
                await self.anti_detection.take_screenshot("venue_page")
            else:
                await self.page.wait_for_timeout(3000)
            
            print("✅ 成功進入時段頁面")
            return True
            
        except Exception as e:
            print(f"❌ 導航到時段頁面失敗: {e}")
            return False
    
    async def apply_time_slots(self):
        """申請所有可用時段"""
        print("⏰ 開始申請可用時段...")
        
        try:
            # 尋找「個人登記」按鈕的選擇器
            personal_register_selectors = [
                '.button_apply[title="個人登記"]',
                'text="個人登記"',
                'button:has-text("個人登記")',
                '[title="個人登記"]'
            ]
            
            # 先確認有多少個可申請時段
            total_slots = 0
            for selector in personal_register_selectors:
                try:
                    buttons = await self.page.query_selector_all(selector)
                    if buttons:
                        total_slots = len(buttons)
                        print(f"✅ 找到 {total_slots} 個可申請時段")
                        break
                except:
                    continue
            
            if total_slots == 0:
                print("⚠️  沒有找到可申請的時段")
                return True  # 沒有可申請時段不算失敗
            
            # 逐一申請每個時段（每次都重新查找按鈕避免 DOM 失效）
            for i in range(total_slots):
                try:
                    print(f"📝 申請第 {i+1} 個時段...")
                    
                    # 重新查找按鈕（避免 DOM 失效）
                    current_buttons = []
                    for selector in personal_register_selectors:
                        try:
                            buttons = await self.page.query_selector_all(selector)
                            if buttons and len(buttons) > i:
                                current_buttons = buttons
                                break
                        except:
                            continue
                    
                    if not current_buttons or i >= len(current_buttons):
                        print(f"⚠️  無法找到第 {i+1} 個時段的按鈕")
                        continue
                    
                    # 使用反檢測點擊
                    if self.anti_detection:
                        # 先截圖當前狀態
                        await self.anti_detection.take_screenshot(f"before_slot_{i+1}")
                        
                        # 點擊個人登記按鈕
                        await current_buttons[i].click()
                        await self.page.wait_for_load_state('networkidle')
                        await self.anti_detection.wait_with_random_delay(2000, 4000)
                        
                        # 截圖申請表單
                        await self.anti_detection.take_screenshot(f"form_slot_{i+1}")
                        
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
                            print("⚠️  無法填寫表演項目")
                        
                        # 等待一下再送出
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
                                    print("🎉 申請成功！")
                                    
                                    # 截圖成功彈跳視窗
                                    await self.anti_detection.take_screenshot(f"success_slot_{i+1}")
                                    
                                    # 點擊確定
                                    confirm_btn = await self.page.wait_for_selector(
                                        'button:has-text("確定")', 
                                        timeout=5000
                                    )
                                    if confirm_btn:
                                        await self.anti_detection.human_like_click(
                                            'button:has-text("確定")', "確認按鈕"
                                        )
                                        
                                        # 重要：等待 5 秒讓頁面跳回日曆頁面
                                        print("⏱️  等待 5 秒讓頁面跳回日曆...")
                                        await self.anti_detection.wait_with_random_delay(5000, 6000)
                                        
                                        self.applied_slots.append(f"時段 {i+1}")
                                        print(f"🎉 第 {i+1} 個時段申請成功！")
                                
                            except Exception as popup_error:
                                print(f"⚠️  處理成功彈跳視窗時發生錯誤: {popup_error}")
                        else:
                            print("❌ 無法點擊送出按鈕")
                    
                    # 每次申請完成後都確保回到日曆頁面（無論成功或失敗）
                    if i < total_slots - 1:  # 如果不是最後一個時段
                        print("🔄 確認回到時段選擇頁面...")
                        current_url = self.page.url
                        if CURRENT_VENUE_URL not in current_url:
                            # 如果不在日曆頁面，重新導航
                            await self.page.goto(CURRENT_VENUE_URL)
                            await self.page.wait_for_load_state('networkidle')
                        
                        if self.anti_detection:
                            await self.anti_detection.wait_with_random_delay(2000, 3000)
                    
                except Exception as slot_error:
                    print(f"❌ 申請第 {i+1} 個時段時發生錯誤: {slot_error}")
                    continue
            
            print(f"✅ 時段申請完成，成功申請: {len(self.applied_slots)} 個時段")
            return True
            
        except Exception as e:
            print(f"❌ 申請時段時發生錯誤: {e}")
            return False
    
    async def take_final_screenshot(self):
        """拍攝最終截圖"""
        print("📸 拍攝最終截圖...")
        
        try:
            if self.anti_detection:
                await self.anti_detection.take_screenshot("final_result", full_page=True)
            else:
                screenshot_path = self.screenshot_dir / "final_result.png"
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"✅ 最終截圖已儲存: {screenshot_path}")
        except Exception as e:
            print(f"⚠️  最終截圖失敗: {e}")
    
    async def cleanup(self):
        """清理資源"""
        if self.anti_detection:
            await self.anti_detection.close_browser()
        else:
            print("✅ 基本清理完成")
    
    async def run_with_retry(self):
        """帶重試機制的主執行流程"""
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n🎯 開始第 {attempt} 次嘗試...")
            print("=" * 60)
            
            try:
                success = await self.run_single_attempt()
                if success:
                    print(f"✅ 第 {attempt} 次嘗試成功！")
                    return True
                else:
                    print(f"❌ 第 {attempt} 次嘗試失敗")
                    
            except Exception as e:
                print(f"❌ 第 {attempt} 次嘗試發生異常: {e}")
            
            # 清理當前嘗試的資源
            await self.cleanup()
            
            # 如果不是最後一次嘗試，等待後重試
            if attempt < MAX_RETRIES:
                print(f"⏱️  等待 {RETRY_DELAY_SECONDS} 秒後重試...")
                await asyncio.sleep(RETRY_DELAY_SECONDS)
        
        print(f"❌ 所有 {MAX_RETRIES} 次嘗試都失敗了")
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
                print("❌ 登入失敗，終止此次嘗試")
                return False
            
            # 導航到場地頁面
            nav_success = await self.navigate_to_venue()
            if not nav_success:
                print("❌ 導航失敗，終止此次嘗試")
                return False
            
            # 申請時段
            apply_success = await self.apply_time_slots()
            if not apply_success:
                print("❌ 申請時段失敗")
                return False
            
            # 拍攝最終截圖
            await self.take_final_screenshot()
            
            # 顯示結果摘要
            self.show_results()
            
            return True
            
        except Exception as e:
            print(f"❌ 執行過程發生錯誤: {e}")
            return False
    
    def show_results(self):
        """顯示申請結果摘要"""
        print("\n" + "="*60)
        print("🎯 申請結果摘要:")
        print(f"✅ 成功申請時段數: {len(self.applied_slots)}")
        if self.applied_slots:
            for slot in self.applied_slots:
                print(f"   - {slot}")
        else:
            print("   - 無可申請時段或申請失敗")
        print(f"📁 截圖位置: {self.screenshot_dir}")
        print("="*60)


async def main():
    """主函數"""
    print("🎯 台北街頭藝人申請系統 (反檢測增強版)")
    print("=" * 60)
    
    app = StreetArtistApplication()
    
    try:
        success = await app.run_with_retry()
        if success:
            print("\n🎉 程式執行成功！")
        else:
            print("\n😞 程式執行失敗，請檢查錯誤訊息")
    
    finally:
        # 確保資源清理
        await app.cleanup()
        print("🧹 資源清理完成")


if __name__ == "__main__":
    asyncio.run(main())
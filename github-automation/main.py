#!/usr/bin/env python3
"""
台北街頭藝人申請系統 - 主程式

簡化版本，用於測試基本流程
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright
from config import (
    TAIPEI_ARTIST_USERNAME,
    TAIPEI_ARTIST_PASSWORD,
    CURRENT_ENTRANCE,
    PERFORMANCE_ITEMS,
    WEBSITE_STRUCTURE_FILE
)


class StreetArtistApplication:
    """街頭藝人申請主程式"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.structure = {}
        self.applied_slots = []
        
    async def load_structure(self):
        """載入網站結構配置"""
        try:
            with open(WEBSITE_STRUCTURE_FILE, 'r', encoding='utf-8') as f:
                self.structure = json.load(f)
            print("✅ 已載入網站結構配置")
        except Exception as e:
            print(f"⚠️  無法載入配置檔: {e}")
            print("🔄 使用預設配置")
            # 簡單的預設配置
            self.structure = {
                "login_flow": {
                    "initial_url": "https://tpbusker.gov.taipei/signin.aspx"
                },
                "venue_selection": {
                    "direct_url": "https://tpbusker.gov.taipei/place.aspx"
                }
            }
    
    async def start_browser(self):
        """啟動瀏覽器"""
        print("🚀 啟動瀏覽器...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)  # 顯示瀏覽器方便調試
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        print("✅ 瀏覽器啟動完成")
    
    async def perform_login(self):
        """執行登入流程"""
        print("🔐 開始登入流程...")
        
        try:
            # 第一步：前往街頭藝人網站（重要：必須先到這裡建立 session）
            initial_url = self.structure.get("login_flow", {}).get("initial_url", "https://tpbusker.gov.taipei/signin.aspx")
            print(f"📍 前往初始頁面: {initial_url}")
            await self.page.goto(initial_url)
            await self.page.wait_for_load_state('networkidle')
            
            # 等待頁面載入並截圖
            await self.page.wait_for_timeout(3000)
            screenshot_path = os.path.expanduser("~/Desktop/debug_step1_initial.png")
            await self.page.screenshot(path=screenshot_path)
            print(f"📸 已截圖: {screenshot_path}")
            
            # 第二步：點擊確定登入（使用更精確的選擇器）
            try:
                # 嘗試多種確定登入的選擇器
                confirm_selectors = [
                    'input[value="確定登入"]',
                    '#ct100_ContentPlaceHolder1_Button1',
                    'input[class="button9"]',
                    'button:has-text("確定登入")',
                    'input:has-text("確定登入")'
                ]
                
                confirm_clicked = False
                for selector in confirm_selectors:
                    try:
                        confirm_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if confirm_btn:
                            await confirm_btn.click()
                            print(f"✅ 已點擊確定登入 (使用選擇器: {selector})")
                            await self.page.wait_for_load_state('networkidle')
                            confirm_clicked = True
                            break
                    except:
                        continue
                
                if not confirm_clicked:
                    print("❌ 無法找到確定登入按鈕")
                    
            except Exception as e:
                print(f"⚠️  點擊確定登入時發生錯誤: {e}")
            
            # 第三步：選擇台北通
            try:
                # 等待台北通選項出現
                await self.page.wait_for_timeout(3000)
                
                # 截圖看當前頁面
                screenshot_path = os.path.expanduser("~/Desktop/debug_step2_choice.png")
                await self.page.screenshot(path=screenshot_path)
                print(f"📸 已截圖選擇頁面: {screenshot_path}")
                
                # 點擊台北通
                taipei_btn = await self.page.wait_for_selector('text="點我登入"', timeout=10000)
                if taipei_btn:
                    await taipei_btn.click()
                    print("✅ 已點擊台北通登入")
                    await self.page.wait_for_load_state('networkidle')
                
            except Exception as e:
                print(f"⚠️  選擇台北通時發生錯誤: {e}")
            
            # 第四步：填入帳號密碼
            try:
                await self.page.wait_for_timeout(3000)
                
                # 截圖登入頁面
                screenshot_path = os.path.expanduser("~/Desktop/debug_step3_login_form.png")
                await self.page.screenshot(path=screenshot_path)
                print(f"📸 已截圖登入表單: {screenshot_path}")
                
                # 填入帳號（嘗試多種選擇器）
                username_selectors = [
                    'input[placeholder*="帳號"]',
                    'input[type="text"]',
                    'input[name*="user"]'
                ]
                
                username_filled = False
                for selector in username_selectors:
                    try:
                        username_field = await self.page.wait_for_selector(selector, timeout=2000)
                        if username_field:
                            await username_field.fill(TAIPEI_ARTIST_USERNAME)
                            print(f"✅ 已填入帳號 (使用選擇器: {selector})")
                            username_filled = True
                            break
                    except:
                        continue
                
                if not username_filled:
                    print("❌ 無法找到帳號欄位")
                
                # 填入密碼
                try:
                    password_field = await self.page.wait_for_selector('input[type="password"]', timeout=5000)
                    if password_field:
                        await password_field.fill(TAIPEI_ARTIST_PASSWORD)
                        print("✅ 已填入密碼")
                except:
                    print("❌ 無法找到密碼欄位")
                
                # 點擊登入按鈕（使用從 DevTools 發現的精確選擇器）
                login_selectors = [
                    'a.green_btn.login_btn',  # 從 DevTools 發現的精確選擇器
                    '.green_btn.login_btn',
                    'a[class="green_btn login_btn"]',
                    'button:has-text("登入")',
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '.btn:has-text("登入")',
                    '[value="登入"]'
                ]
                
                login_clicked = False
                for selector in login_selectors:
                    try:
                        login_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if login_btn:
                            # 檢查按鈕文字是否包含登入
                            btn_text = await login_btn.text_content()
                            if "登入" in btn_text or selector == 'button':  # 如果是通用按鈕選擇器，直接點擊
                                await login_btn.click()
                                print(f"✅ 已點擊登入按鈕 (使用選擇器: {selector})")
                                await self.page.wait_for_load_state('networkidle')
                                
                                # 等待登入完成
                                await self.page.wait_for_timeout(5000)
                                
                                # 截圖登入後頁面
                                screenshot_path = os.path.expanduser("~/Desktop/debug_step4_after_login.png")
                                await self.page.screenshot(path=screenshot_path)
                                print(f"📸 已截圖登入後頁面: {screenshot_path}")
                                
                                login_clicked = True
                                break
                    except:
                        continue
                
                if not login_clicked:
                    print("❌ 無法找到登入按鈕")
                
            except Exception as e:
                print(f"⚠️  登入表單填寫時發生錯誤: {e}")
            
            print("✅ 登入流程完成")
            
        except Exception as e:
            print(f"❌ 登入流程發生錯誤: {e}")
    
    async def navigate_to_venue(self):
        """直接導航到大安森林公園時段頁面"""
        print("🏢 直接前往大安森林公園時段頁面...")
        
        try:
            # 直接前往大安森林公園2號門入口的時段頁面
            direct_url = "https://tpbusker.gov.taipei/apply.aspx?pl=9&loc=67"
            print(f"📍 直接前往時段頁面: {direct_url}")
            await self.page.goto(direct_url)
            await self.page.wait_for_load_state('networkidle')
            
            # 等待頁面載入
            await self.page.wait_for_timeout(3000)
            
            # 截圖時段頁面
            screenshot_path = os.path.expanduser("~/Desktop/debug_step5_timeslot_page.png")
            await self.page.screenshot(path=screenshot_path)
            print(f"📸 已截圖時段頁面: {screenshot_path}")
            
            print("✅ 時段頁面載入完成")
            
        except Exception as e:
            print(f"❌ 導航到時段頁面失敗: {e}")
    
    async def select_entrance_and_apply(self):
        """檢查時段頁面是否載入正確"""
        print(f"🎯 檢查時段頁面 (已直接進入 {CURRENT_ENTRANCE})...")
        
        try:
            # 檢查是否成功載入時段頁面
            page_title = await self.page.title()
            current_url = self.page.url
            print(f"📍 當前頁面標題: {page_title}")
            print(f"📍 當前頁面 URL: {current_url}")
            
            # 檢查是否在正確的時段頁面
            if "apply.aspx" in current_url:
                print("✅ 成功進入時段申請頁面")
            else:
                print("⚠️  可能未正確進入時段頁面")
            
        except Exception as e:
            print(f"❌ 檢查時段頁面時發生錯誤: {e}")
    
    async def apply_time_slots(self):
        """申請所有可用時段"""
        print("⏰ 開始申請時段...")
        
        try:
            # 使用從截圖中發現的正確選擇器尋找「個人登記」按鈕
            personal_register_selectors = [
                '.button_apply[title="個人登記"]',  # 從DevTools看到的精確選擇器
                'text="個人登記"',
                'button:has-text("個人登記")',
                '[title="個人登記"]'
            ]
            
            personal_register_buttons = []
            for selector in personal_register_selectors:
                try:
                    buttons = await self.page.query_selector_all(selector)
                    if buttons:
                        personal_register_buttons = buttons
                        print(f"✅ 使用選擇器 {selector} 找到 {len(buttons)} 個個人登記按鈕")
                        break
                except:
                    continue
            
            if not personal_register_buttons:
                print("⚠️  沒有找到可申請的時段")
                return
            
            print(f"🔍 找到 {len(personal_register_buttons)} 個可申請時段")
            
            # 逐一申請每個時段
            for i, button in enumerate(personal_register_buttons):
                try:
                    print(f"📝 申請第 {i+1} 個時段...")
                    
                    # 點擊個人登記按鈕
                    await button.click()
                    await self.page.wait_for_load_state('networkidle')
                    
                    # 等待申請表單載入
                    await self.page.wait_for_timeout(2000)
                    
                    # 截圖申請表單
                    screenshot_path = os.path.expanduser(f"~/Desktop/debug_step6_form_{i+1}.png")
                    await self.page.screenshot(path=screenshot_path)
                    print(f"📸 已截圖申請表單: {screenshot_path}")
                    
                    # 填寫表演項目
                    performance_selectors = [
                        'textarea',
                        'textarea[name*="項目"]',
                        'input[name*="項目"]'
                    ]
                    
                    performance_filled = False
                    for perf_selector in performance_selectors:
                        try:
                            performance_field = await self.page.wait_for_selector(perf_selector, timeout=3000)
                            if performance_field:
                                await performance_field.fill(PERFORMANCE_ITEMS)
                                print(f"✅ 已填入表演項目: {PERFORMANCE_ITEMS}")
                                performance_filled = True
                                break
                        except:
                            continue
                    
                    if not performance_filled:
                        print("⚠️  無法找到表演項目欄位")
                    
                    # 點擊確定送出
                    submit_selectors = [
                        'button:has-text("確定送出")',
                        'input[value="確定送出"]',
                        'button:has-text("送出")',
                        'input[type="submit"]'
                    ]
                    
                    submit_clicked = False
                    for submit_selector in submit_selectors:
                        try:
                            submit_btn = await self.page.wait_for_selector(submit_selector, timeout=3000)
                            if submit_btn:
                                await submit_btn.click()
                                print(f"✅ 已點擊送出按鈕 (使用選擇器: {submit_selector})")
                                submit_clicked = True
                                break
                        except:
                            continue
                    
                    if submit_clicked:
                        # 等待成功彈跳視窗
                        try:
                            success_popup = await self.page.wait_for_selector('text="個人登記(需管理者審核通過)完成!"', timeout=10000)
                            if success_popup:
                                print("🎉 申請成功！")
                                
                                # 截圖成功彈跳視窗
                                screenshot_path = os.path.expanduser(f"~/Desktop/debug_step7_success_{i+1}.png")
                                await self.page.screenshot(path=screenshot_path)
                                print(f"📸 已截圖成功彈跳視窗: {screenshot_path}")
                                
                                # 點擊確定
                                confirm_btn = await self.page.wait_for_selector('button:has-text("確定")', timeout=5000)
                                if confirm_btn:
                                    await confirm_btn.click()
                                    print("✅ 已確認成功訊息")
                                    
                                    # 等待回到日曆頁面
                                    await self.page.wait_for_timeout(5000)
                                    
                                    self.applied_slots.append(f"時段 {i+1}")
                            
                        except Exception as popup_error:
                            print(f"⚠️  處理成功彈跳視窗時發生錯誤: {popup_error}")
                    else:
                        print("❌ 無法找到送出按鈕")
                    
                    # 回到時段選擇頁面（如果不是最後一個）
                    if i < len(personal_register_buttons) - 1:
                        print("🔄 返回時段選擇頁面...")
                        # 重新導航到時段頁面
                        await self.page.goto("https://tpbusker.gov.taipei/apply.aspx?pl=9&loc=67")
                        await self.page.wait_for_load_state('networkidle')
                        await self.page.wait_for_timeout(2000)
                        
                        # 重新取得按鈕列表
                        for selector in personal_register_selectors:
                            try:
                                buttons = await self.page.query_selector_all(selector)
                                if buttons:
                                    personal_register_buttons = buttons
                                    break
                            except:
                                continue
                    
                except Exception as slot_error:
                    print(f"❌ 申請第 {i+1} 個時段時發生錯誤: {slot_error}")
                    continue
            
            print(f"✅ 時段申請完成，成功申請: {len(self.applied_slots)} 個時段")
            
        except Exception as e:
            print(f"❌ 申請時段時發生錯誤: {e}")
    
    async def take_final_screenshot(self):
        """拍攝最終截圖"""
        print("📸 拍攝最終截圖...")
        
        try:
            screenshot_path = os.path.expanduser("~/Desktop/final_result.png")
            await self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ 最終截圖已儲存: {screenshot_path}")
        except Exception as e:
            print(f"⚠️  截圖失敗: {e}")
    
    async def close_browser(self):
        """關閉瀏覽器"""
        if self.browser:
            await self.browser.close()
            print("✅ 瀏覽器已關閉")
    
    async def run(self):
        """執行完整流程"""
        try:
            await self.load_structure()
            await self.start_browser()
            await self.perform_login()
            await self.navigate_to_venue()
            await self.select_entrance_and_apply()
            await self.apply_time_slots()
            await self.take_final_screenshot()
            
            # 顯示結果
            print("\n" + "="*50)
            print("🎯 申請結果摘要:")
            print(f"✅ 成功申請時段數: {len(self.applied_slots)}")
            for slot in self.applied_slots:
                print(f"   - {slot}")
            print("="*50)
            
        except Exception as e:
            print(f"❌ 執行過程發生錯誤: {e}")
        
        finally:
            await self.close_browser()


async def main():
    """主函數"""
    print("🎯 台北街頭藝人申請系統")
    print("=" * 50)
    
    app = StreetArtistApplication()
    await app.run()
    
    print("🎉 程式執行完成！")


if __name__ == "__main__":
    asyncio.run(main())

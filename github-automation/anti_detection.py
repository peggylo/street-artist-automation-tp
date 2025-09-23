#!/usr/bin/env python3
"""
台北街頭藝人申請系統 - 反檢測模組

實作瀏覽器自動化反檢測技術，包括：
- Profile 管理
- 養軌跡策略  
- 人類行為模擬
"""

import asyncio
import random
import tempfile
import shutil
import os
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class AntiDetectionManager:
    """反檢測管理器"""
    
    def __init__(self, headless=True, screenshot_dir="screenshots"):
        self.headless = headless
        self.screenshot_dir = Path(screenshot_dir)
        self.profile_dir = None
        self.browser = None
        self.context = None
        self.page = None
        
        # 確保截圖目錄存在
        self.screenshot_dir.mkdir(exist_ok=True)
        
    async def create_browser_profile(self):
        """建立臨時瀏覽器 Profile"""
        print("🏗️  建立臨時瀏覽器 Profile...")
        
        # 建立臨時資料夾
        self.profile_dir = Path(tempfile.mkdtemp(prefix="street-artist-profile-"))
        print(f"📁 Profile 位置: {self.profile_dir}")
        
        return self.profile_dir
    
    async def cleanup_profile(self):
        """清理臨時 Profile"""
        if self.profile_dir and self.profile_dir.exists():
            try:
                shutil.rmtree(self.profile_dir)
                print(f"🧹 已清理 Profile: {self.profile_dir}")
            except Exception as e:
                print(f"⚠️  清理 Profile 時發生錯誤: {e}")
    
    async def start_browser(self):
        """啟動具有反檢測功能的瀏覽器"""
        print("🚀 啟動反檢測瀏覽器...")
        
        # 建立 Profile
        await self.create_browser_profile()
        
        playwright = await async_playwright().start()
        
        # 反檢測啟動參數
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding"
        ]
        
        # 使用持久化上下文
        self.context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=self.headless,
            channel="chrome",
            args=args,
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 建立新頁面
        self.page = await self.context.new_page()
        
        # 移除 webdriver 屬性
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print("✅ 反檢測瀏覽器啟動完成")
        return self.page
    
    async def perform_trajectory_building(self):
        """執行養軌跡流程"""
        print("🎪 開始建立瀏覽軌跡...")
        
        if not self.page:
            raise Exception("瀏覽器未啟動")
        
        # 養軌跡網站列表
        trajectory_sites = [
            {
                "url": "https://www.taipei.gov.tw/",
                "name": "台北市政府首頁",
                "stay_time": (15, 25),
                "actions": ["scroll"]
            },
            {
                "url": "https://www.taipei.gov.tw/cp.aspx?n=6B8CE5C7B7E9C13F",
                "name": "市民服務專區", 
                "stay_time": (20, 30),
                "actions": ["scroll", "hover_links"]
            },
            {
                "url": "https://www.taipei.gov.tw/cp.aspx?n=BD5C76C080A3B1F8",
                "name": "線上申辦服務",
                "stay_time": (15, 20),
                "actions": ["scroll"]
            }
        ]
        
        for i, site in enumerate(trajectory_sites):
            print(f"📍 瀏覽第 {i+1} 個網站: {site['name']}")
            
            try:
                # 前往網站
                await self.page.goto(site['url'], wait_until='networkidle')
                
                # 等待頁面載入
                await self.page.wait_for_timeout(random.randint(2000, 4000))
                
                # 截圖記錄
                screenshot_path = self.screenshot_dir / f"trajectory_{i+1}_{site['name'].replace(' ', '_')}.png"
                await self.page.screenshot(path=str(screenshot_path))
                print(f"📸 已截圖: {screenshot_path}")
                
                # 執行隨機動作
                if "scroll" in site['actions']:
                    await self.simulate_scrolling()
                
                if "hover_links" in site['actions']:
                    await self.simulate_link_hovering()
                
                # 停留時間
                stay_time = random.randint(site['stay_time'][0], site['stay_time'][1])
                print(f"⏱️  停留 {stay_time} 秒...")
                await self.page.wait_for_timeout(stay_time * 1000)
                
                # 頁面間隔
                if i < len(trajectory_sites) - 1:
                    interval = random.randint(5, 10)
                    print(f"🔄 等待 {interval} 秒後前往下一個網站...")
                    await self.page.wait_for_timeout(interval * 1000)
                
            except Exception as e:
                print(f"⚠️  瀏覽 {site['name']} 時發生錯誤: {e}")
                continue
        
        print("✅ 瀏覽軌跡建立完成")
    
    async def simulate_scrolling(self):
        """模擬自然的滾動行為"""
        # 隨機滾動 2-4 次
        scroll_times = random.randint(2, 4)
        
        for _ in range(scroll_times):
            # 隨機滾動距離
            scroll_distance = random.randint(200, 600)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            
            # 滾動間隔
            await self.page.wait_for_timeout(random.randint(1000, 2500))
    
    async def simulate_link_hovering(self):
        """模擬滑鼠懸停連結"""
        try:
            # 尋找可見的連結
            links = await self.page.query_selector_all("a:visible")
            if links and len(links) > 0:
                # 隨機選擇 1-2 個連結懸停
                hover_count = min(random.randint(1, 2), len(links))
                selected_links = random.sample(links, hover_count)
                
                for link in selected_links:
                    try:
                        await link.hover()
                        await self.page.wait_for_timeout(random.randint(500, 1500))
                    except:
                        continue
        except Exception as e:
            # 懸停失敗不影響主流程
            pass
    
    async def human_like_click(self, selector, description="元素"):
        """模擬人類點擊行為"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=10000)
            if element:
                # 先移動到元素附近
                box = await element.bounding_box()
                if box:
                    # 隨機偏移點擊位置
                    offset_x = random.randint(-5, 5)
                    offset_y = random.randint(-5, 5)
                    
                    target_x = box['x'] + box['width']/2 + offset_x
                    target_y = box['y'] + box['height']/2 + offset_y
                    
                    # 模擬滑鼠移動軌跡
                    await self.page.mouse.move(target_x, target_y)
                    await self.page.wait_for_timeout(random.randint(100, 300))
                    
                    # 點擊
                    await element.click()
                    print(f"✅ 已點擊{description}")
                    return True
        except Exception as e:
            print(f"❌ 點擊{description}失敗: {e}")
            return False
        
        return False
    
    async def human_like_type(self, selector, text, description="欄位"):
        """模擬人類打字行為"""
        try:
            field = await self.page.wait_for_selector(selector, timeout=10000)
            if field:
                # 先點擊欄位
                await field.click()
                await self.page.wait_for_timeout(random.randint(200, 500))
                
                # 清空欄位
                await field.fill("")
                
                # 逐字輸入
                for char in text:
                    await self.page.keyboard.type(char)
                    # 隨機打字速度
                    await self.page.wait_for_timeout(random.randint(50, 150))
                
                print(f"✅ 已填入{description}: {text}")
                return True
        except Exception as e:
            print(f"❌ 填入{description}失敗: {e}")
            return False
        
        return False
    
    async def take_screenshot(self, name, full_page=False):
        """拍攝截圖"""
        try:
            screenshot_path = self.screenshot_dir / f"{name}.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=full_page)
            print(f"📸 已截圖: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            print(f"⚠️  截圖失敗: {e}")
            return None
    
    async def wait_with_random_delay(self, min_ms=1000, max_ms=3000):
        """隨機延遲等待"""
        delay = random.randint(min_ms, max_ms)
        await self.page.wait_for_timeout(delay)
    
    async def close_browser(self):
        """關閉瀏覽器並清理"""
        if self.context:
            await self.context.close()
            print("✅ 瀏覽器已關閉")
        
        await self.cleanup_profile()


class LoginAntiDetection:
    """專門處理登入階段的反檢測"""
    
    def __init__(self, anti_detection_manager: AntiDetectionManager):
        self.adm = anti_detection_manager
        self.page = anti_detection_manager.page
    
    async def perform_enhanced_login(self, username, password):
        """執行增強版登入流程"""
        print("🔐 開始增強版登入流程...")
        
        try:
            # 第一步：前往街頭藝人網站
            initial_url = "https://tpbusker.gov.taipei/signin.aspx"
            print(f"📍 前往登入頁面: {initial_url}")
            await self.page.goto(initial_url, wait_until='networkidle')
            await self.adm.wait_with_random_delay(2000, 4000)
            await self.adm.take_screenshot("step1_initial_page")
            
            # 第二步：點擊確定登入
            confirm_selectors = [
                'input[value="確定登入"]',
                '#ct100_ContentPlaceHolder1_Button1',
                'input[class="button9"]'
            ]
            
            confirm_success = False
            for selector in confirm_selectors:
                if await self.adm.human_like_click(selector, "確定登入按鈕"):
                    confirm_success = True
                    break
            
            if not confirm_success:
                print("❌ 無法找到確定登入按鈕")
                return False
            
            await self.page.wait_for_load_state('networkidle')
            await self.adm.wait_with_random_delay(2000, 4000)
            await self.adm.take_screenshot("step2_after_confirm")
            
            # 第三步：選擇台北通
            taipei_selectors = [
                'text="點我登入"',
                'a:has-text("點我登入")'
            ]
            
            taipei_success = False
            for selector in taipei_selectors:
                if await self.adm.human_like_click(selector, "台北通登入"):
                    taipei_success = True
                    break
            
            if not taipei_success:
                print("❌ 無法找到台北通登入按鈕")
                return False
            
            await self.page.wait_for_load_state('networkidle')
            await self.adm.wait_with_random_delay(3000, 5000)
            await self.adm.take_screenshot("step3_taipei_login_page")
            
            # 第四步：填入帳號密碼
            # 填入帳號
            username_selectors = [
                'input[placeholder*="帳號"]',
                'input[type="text"]',
                'input[name*="user"]'
            ]
            
            username_success = False
            for selector in username_selectors:
                if await self.adm.human_like_type(selector, username, "帳號"):
                    username_success = True
                    break
            
            if not username_success:
                print("❌ 無法填入帳號")
                return False
            
            await self.adm.wait_with_random_delay(500, 1000)
            
            # 填入密碼
            password_success = await self.adm.human_like_type('input[type="password"]', password, "密碼")
            if not password_success:
                print("❌ 無法填入密碼")
                return False
            
            await self.adm.wait_with_random_delay(1000, 2000)
            await self.adm.take_screenshot("step4_credentials_filled")
            
            # 第五步：點擊登入
            login_selectors = [
                'a.green_btn.login_btn',
                '.green_btn.login_btn',
                'a[class="green_btn login_btn"]'
            ]
            
            login_success = False
            for selector in login_selectors:
                if await self.adm.human_like_click(selector, "登入按鈕"):
                    login_success = True
                    break
            
            if not login_success:
                print("❌ 無法點擊登入按鈕")
                return False
            
            # 等待登入結果
            await self.page.wait_for_load_state('networkidle')
            await self.adm.wait_with_random_delay(3000, 6000)
            await self.adm.take_screenshot("step5_login_result")
            
            # 檢查是否登入成功
            current_url = self.page.url
            if "signin.aspx" not in current_url:
                print("✅ 登入成功！")
                return True
            else:
                print("❌ 登入失敗，可能被機器人檢測阻擋")
                return False
                
        except Exception as e:
            print(f"❌ 登入過程發生錯誤: {e}")
            await self.adm.take_screenshot("login_error")
            return False

# -- coding: utf-8 --
"""
Copyright (c) 2024 [Hosea]
Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
from datetime import datetime, timezone, timedelta
import traceback
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class Config:
    """配置类 - 统一管理所有环境变量"""
    
    def __init__(self):
        # Cookie 配置（支持多账号，用 | 分隔）
        raw_cookie = os.environ.get("NS_COOKIE") or os.environ.get("COOKIE") or ""
        self.cookies = [c.strip() for c in raw_cookie.split("|") if c.strip()]
        
        # 基础配置
        self.ns_random = os.environ.get("NS_RANDOM", "false").lower() == "true"
        self.headless = os.environ.get("HEADLESS", "true").lower() == "true"
        
        # Telegram 通知配置
        self.tg_bot_token = os.environ.get("TG_BOT_TOKEN")
        self.tg_chat_id = os.environ.get("TG_CHAT_ID")
        
        # 评论区域配置（处理空字符串）
        comment_url_env = os.environ.get("NS_COMMENT_URL", "") or ""
        self.comment_url = comment_url_env.strip() if comment_url_env.strip() else "https://www.nodeseek.com/categories/trade"
        
        # 随机延迟配置（分钟）
        delay_min_str = os.environ.get("NS_DELAY_MIN", "") or "0"
        delay_max_str = os.environ.get("NS_DELAY_MAX", "") or "30"
        self.delay_min = int(delay_min_str)
        self.delay_max = int(delay_max_str)
    
    @property
    def account_count(self):
        return len(self.cookies)
    
    def get_random_delay_seconds(self):
        """获取随机延迟秒数"""
        if self.delay_max <= 0:
            return 0
        # 确保 min <= max
        actual_min = min(self.delay_min, self.delay_max)
        actual_max = max(self.delay_min, self.delay_max)
        delay_minutes = random.randint(actual_min, actual_max)
        return delay_minutes * 60


# 全局配置实例
config = Config()

# 随机评论内容
randomInputStr = ["bd","绑定","帮顶","吃瓜吃瓜","好价","过来看一下","喝杯奶茶压压惊","咕噜咕噜","前排","悄悄地我来了悄悄地又走了","恭喜发财","好基","公道公道","楼主不错 绑定","还可以","再看看吧","楼下要了","挺不错的 bdbd","好价 好价","给楼下点个","祝早出","观望一下 早出","让给楼下","bd 可惜用不上 楼下来秒了","还要啥自行车","卷起来","就是这个feel","这是什么东西","吗喽~~~","收了吧楼下","bd一下","bd"]

def send_telegram_message(message):
    """
    发送 Telegram 消息通知
    如果未配置 TG_BOT_TOKEN 或 TG_CHAT_ID，则静默跳过
    """
    if not config.tg_bot_token or not config.tg_chat_id:
        print("未配置 Telegram 通知，跳过发送")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{config.tg_bot_token}/sendMessage"
        payload = {
            "chat_id": config.tg_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Telegram 通知发送成功")
            return True
        else:
            print(f"Telegram 通知发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"Telegram 通知发送出错: {str(e)}")
        return False

def send_telegram_photo(photo_path, caption=None):
    """
    发送图片到 Telegram
    """
    if not config.tg_bot_token or not config.tg_chat_id:
        return False
        
    try:
        url = f"https://api.telegram.org/bot{config.tg_bot_token}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            payload = {'chat_id': config.tg_chat_id}
            if caption:
                payload['caption'] = caption
            files = {'photo': photo}
            response = requests.post(url, data=payload, files=files, timeout=20)
            
        if response.status_code == 200:
            print("Telegram 图片发送成功")
            return True
        else:
            print(f"Telegram 图片发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"Telegram 图片发送出错: {str(e)}")
        return False

def retry(max_attempts=3, delay=5):
    """
    重试装饰器
    :param max_attempts: 最大重试次数
    :param delay: 重试间隔（秒）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"[{func.__name__}] 第 {attempt + 1} 次尝试失败: {str(e)}")
                        print(f"等待 {delay} 秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"[{func.__name__}] 已达最大重试次数 ({max_attempts})")
            raise last_exception
        return wrapper
    return decorator

def check_login_status(driver):
    """
    检测 Cookie 是否有效（用户是否已登录）
    返回: True 表示已登录，False 表示未登录或 Cookie 过期
    """
    try:
        print("正在检测登录状态...")
        # 尝试查找用户头像或用户相关元素
        user_elements = driver.find_elements(By.CSS_SELECTOR, '.avatar, .nsk-user-avatar, [class*="avatar"]')
        
        # 也检查是否存在登录按钮（未登录时会显示）
        login_buttons = driver.find_elements(By.XPATH, "//span[contains(text(), '登录')]")
        
        if len(user_elements) > 0 and len(login_buttons) == 0:
            print("✅ 登录状态有效")
            return True
        else:
            print("❌ Cookie 已过期或未登录")
            return False
    except Exception as e:
        print(f"检测登录状态时出错: {str(e)}")
        return False

@retry(max_attempts=3, delay=5)
def click_sign_icon(driver):
    """
    尝试点击签到图标并完成签到
    返回: 
    - "success": 签到成功
    - "already": 今日已签到
    - "failed": 失败
    """
    try:
        print("开始查找签到图标...")
        
        # 方案 A: 直接跳转到签到页面
        print("直接访问签到页面...")
        driver.get("https://www.nodeseek.com/board")
        time.sleep(3)
        
        current_url = driver.current_url
        print(f"当前页面URL: {current_url}")
        
        # 0. 检查 Cloudflare
        if "Just a moment" in driver.title or "Attention Required" in driver.title:
            print("❌ 检测到 Cloudflare 拦截")
            driver.save_screenshot("cf_block_sign.png")
            send_telegram_photo("cf_block_sign.png", caption="❌ 签到时遭遇 Cloudflare 拦截")
            return "failed"
            
        # 1. 检查是否被重定向回首页
        if "/board" not in current_url and "nodeseek.com" in current_url and len(current_url) < 30:
            print("⚠️ 似乎跳转回了首页，尝试在首页寻找签到入口...")
            try:
                sign_icon = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@title='签到']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sign_icon)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", sign_icon)
                print("首页签到图标点击成功")
                time.sleep(3)
            except Exception as e:
                print(f"首页签到图标未找到: {str(e)}")
        
        # 2. 尝试定位签到面板（.board-intro）
        try:
            board_intro = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".board-intro"))
            )
            print("签到面板加载成功")
            
            # 检查面板文本
            intro_text = board_intro.text
            print(f"面板文本内容: {intro_text}")
            
            # 优先检查是否存在"已签到"关键词
            if "获得" in intro_text or "排名" in intro_text or "已签到" in intro_text:
                print("✅ 检测到已签到关键词")
                return "already"
            
            # 检查是否有按钮
            buttons = board_intro.find_elements(By.TAG_NAME, "button")
            if buttons:
                print(f"发现 {len(buttons)} 个按钮，尝试点击...")
                target_button = buttons[0]
                for btn in buttons:
                    text = btn.text
                    if "手气" in text or "鸡腿" in text:
                        target_button = btn
                        break
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", target_button)
                print("签到按钮点击成功")
                time.sleep(2)
                return "success"
                
            if "还未签到" in intro_text:
                print("❌ 检测到'还未签到'文本，但未找到按钮")
                return "failed"
                
            print("❌ 无法确认签到状态 (面板无按钮且无明确已签到文本)")
            return "failed"

        except TimeoutException:
            print("⚠️ 未找到签到面板 (.board-intro)，尝试全局文本搜索...")
            
            # 3. 兜底策略：全局搜索文本
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if "今日已签到" in page_text or "签到成功" in page_text or "本次获得" in page_text:
                print("✅ 全局文本检测到 '已签到' 相关字样")
                return "already"
                
            if "登录" in page_text and "注册" in page_text and "个人中心" not in page_text:
                print("❌ 检测到页面包含'登录/注册'，可能是Cookie失效")
                return "failed"

            print("❌ 无法确认签到状态")
            screenshot_path = "sign_intro_error.png"
            driver.save_screenshot(screenshot_path)
            send_telegram_photo(screenshot_path, caption=f"❌ 签到状态未知\nURL: {current_url}")
            return "failed"
            
    except Exception as e:
        print(f"签到过程中出错: {str(e)}")
        traceback.print_exc()
        try:
            driver.save_screenshot("sign_exception.png")
            send_telegram_photo("sign_exception.png", caption=f"❌ 签到异常: {str(e)}")
        except:
            pass
        return "failed"

def setup_driver_and_cookies(cookie_str):
    """
    初始化浏览器并设置cookie的通用方法
    :param cookie_str: Cookie 字符串
    返回: 设置好cookie的driver实例
    """
    try:
        if not cookie_str:
            print("未找到cookie配置")
            return None
            
        print("开始初始化浏览器...")
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        
        if config.headless:
            print("启用无头模式...")
            options.add_argument('--headless=new')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 禁用自动化控制标记
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        print("正在启动Chrome...")
        # 使用 webdriver-manager 自动管理 ChromeDriver 版本
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 修改 webdriver 标记
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        if config.headless:
            driver.set_window_size(1920, 1080)
        
        print("Chrome启动成功")
        
        print("正在设置cookie...")
        driver.get('https://www.nodeseek.com')
        
        # 等待页面加载完成
        time.sleep(5)
        
        for cookie_item in cookie_str.split(';'):
            try:
                name, value = cookie_item.strip().split('=', 1)
                driver.add_cookie({
                    'name': name, 
                    'value': value, 
                    'domain': '.nodeseek.com',
                    'path': '/'
                })
            except Exception as e:
                print(f"设置cookie出错: {str(e)}")
                continue
        
        print("刷新页面...")
        driver.refresh()
        time.sleep(5)  # 增加等待时间
        
        return driver
        
    except Exception as e:
        print(f"设置浏览器和Cookie时出错: {str(e)}")
        print("详细错误信息:")
        print(traceback.format_exc())
        return None

def nodeseek_comment(driver):
    """执行评论任务，返回成功评论数量"""
    comment_count = 0
    try:
        print(f"正在访问评论区域: {config.comment_url}")
        driver.get(config.comment_url)
        print("等待页面加载...")
        
        # 获取初始帖子列表
        posts = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.post-list-item'))
        )
        print(f"成功获取到 {len(posts)} 个帖子")
        
        # 过滤掉置顶帖
        valid_posts = [post for post in posts if not post.find_elements(By.CSS_SELECTOR, '.pined')]
        # 随机选择 5-10 个帖子
        post_count = random.randint(5, 10)
        selected_posts = random.sample(valid_posts, min(post_count, len(valid_posts)))
        
        # 存储已选择的帖子URL
        selected_urls = []
        for post in selected_posts:
            try:
                post_link = post.find_element(By.CSS_SELECTOR, '.post-title a')
                selected_urls.append(post_link.get_attribute('href'))
            except:
                continue
        
        # 使用URL列表进行操作
        for i, post_url in enumerate(selected_urls):
            try:
                print(f"正在处理第 {i+1} 个帖子")
                driver.get(post_url)
                
                # 等待 CodeMirror 编辑器加载
                editor = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.CodeMirror'))
                )
                
                # 点击编辑器区域获取焦点
                editor.click()
                time.sleep(0.5)
                input_text = random.choice(randomInputStr)

                # 模拟输入
                actions = ActionChains(driver)
                # 随机输入 randomInputStr
                for char in input_text:
                    actions.send_keys(char)
                    actions.pause(random.uniform(0.1, 0.3))
                actions.perform()
                
                # 等待一下确保内容已经输入
                time.sleep(2)
                
                # 使用更精确的选择器定位提交按钮
                submit_button = WebDriverWait(driver, 30).until(
                 EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'submit') and contains(@class, 'btn') and contains(text(), '发布评论')]"))
                )
                # 确保按钮可见
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                time.sleep(0.5)
                # 使用 JavaScript 点击避免遮挡问题
                driver.execute_script("arguments[0].click();", submit_button)
                
                print(f"已在帖子 {post_url} 中完成评论")
                comment_count += 1
                
                # 随机等待 3-7 分钟后处理下一个帖子
                wait_minutes = random.uniform(3, 7)
                print(f"等待 {wait_minutes:.1f} 分钟后继续...")
                time.sleep(wait_minutes * 60)
                
            except Exception as e:
                print(f"处理帖子时出错: {str(e)}")
                # 尝试截图分析
                try:
                    screenshot_path = f"comment_error_{i}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"已保存错误截图: {screenshot_path}")
                    # 只发送第一张评论错误截图，避免刷屏
                    if i == 0:
                        send_telegram_photo(screenshot_path, caption=f"❌ 评论失败截图\n帖子: {post_url}\n错误: {str(e)}")
                except:
                    pass
                continue
                
        print("评论任务完成")
        return comment_count
                
    except Exception as e:
        print(f"NodeSeek评论出错: {str(e)}")
        print("详细错误信息:")
        # 尝试截图分析
        try:
            screenshot_path = "comment_main_error.png"
            driver.save_screenshot(screenshot_path)
            send_telegram_photo(screenshot_path, caption=f"❌ 评论任务致命错误\n错误: {str(e)}")
        except:
            pass
            
        traceback.print_exc()
        return comment_count


def run_for_account(cookie_str, account_index):
    """为单个账号执行任务"""
    result = {
        "sign_in": "failed",
        "comments": 0,
        "error": None
    }
    
    print(f"\n{'='*50}")
    print(f"开始处理账号 {account_index + 1}")
    print(f"{'='*50}")
    
    driver = setup_driver_and_cookies(cookie_str)
    if not driver:
        result["error"] = "浏览器初始化失败"
        return result
    
    try:
        # 检测登录状态
        if not check_login_status(driver):
            result["error"] = "Cookie 已过期"
            return result
        
        # 执行签到任务
        result["sign_in"] = click_sign_icon(driver)
        
        # 执行评论任务
        # result["comments"] = nodeseek_comment(driver)
        
    finally:
        try:
            driver.quit()
        except:
            pass
    
    return result


if __name__ == "__main__":
    print("开始执行 NodeSeek 自动任务...")
    
    # 检查配置
    if config.account_count == 0:
        print("未配置 Cookie，退出")
        send_telegram_message("❌ <b>NodeSeek 自动任务失败</b>\n\n未配置 NS_COOKIE 环境变量")
        exit(1)
    
    print(f"检测到 {config.account_count} 个账号")
    
    # 随机延迟执行
    # delay_seconds = config.get_random_delay_seconds()
    # if delay_seconds > 0:
    #     delay_minutes = delay_seconds / 60
    #     print(f"随机延迟执行: 等待 {delay_minutes:.1f} 分钟...")
    #     time.sleep(delay_seconds)
    
    # 为每个账号执行任务
    all_results = []
    for i, cookie in enumerate(config.cookies):
        result = run_for_account(cookie, i)
        all_results.append(result)
    
    print(f"\n{'='*50}")
    print("所有账号任务执行完成")
    print(f"{'='*50}")
    
    # 获取北京时间 (UTC+8)
    beijing_tz = timezone(timedelta(hours=8))
    beijing_time = datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建汇报消息
    if config.account_count == 1:
        # 单账号汇报
        r = all_results[0]
        if r["error"]:
            report_message = f"""❌ <b>NodeSeek 自动任务失败</b>

错误: {r["error"]}

⏰ 执行时间: 北京时间 {beijing_time}"""
        else:
            if r["sign_in"] == "success":
                sign_status = "✅ 成功"
            elif r["sign_in"] == "already":
                sign_status = "🟡 已签到"
            else:
                sign_status = "❌ 失败"
                
            report_message = f"""🎯 <b>NodeSeek 自动任务完成</b>

📝 <b>签到状态:</b> {sign_status}
💬 <b>评论数量:</b> {r["comments"]} 条

⏰ 执行时间: 北京时间 {beijing_time}"""
    else:
        # 多账号汇报
        lines = ["🎯 <b>NodeSeek 多账号任务完成</b>\n"]
        for i, r in enumerate(all_results):
            if r["error"]:
                lines.append(f"❌ 账号{i+1}: {r['error']}")
            else:
                if r["sign_in"] == "success":
                    sign = "✅"
                elif r["sign_in"] == "already":
                    sign = "🟡"
                else:
                    sign = "❌"
                lines.append(f"👤 账号{i+1}: 签到{sign} | 评论{r['comments']}条")
        lines.append(f"\n⏰ 执行时间: 北京时间 {beijing_time}")
        report_message = "\n".join(lines)
    
    send_telegram_message(report_message)

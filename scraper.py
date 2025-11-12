"""
網頁爬蟲模組
"""

import re
import time
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def scrape_books() -> List[Dict[str, Any]]:
    """
    從博客來網站爬取搜尋關鍵字「LLM」的所有書籍資料。
    
    操作流程：
    1. 開啟博客來首頁
    2. 在搜尋框輸入 "LLM"
    3. 提交搜尋
    4. 點選「圖書」分類
    5. 爬取所有分頁的書籍資料
    
    爬取資料包含：
    - title: 書名
    - author: 作者
    - price: 價格（整數）
    - link: 書籍連結
    
    回傳:
        List[Dict[str, Any]]: 書籍資料列表
    """
    # 博客來首頁
    homepage_url = 'https://www.books.com.tw/'
    
    # 設定 Chrome 選項
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    
    books = []
    
    try:
        driver = webdriver.Chrome(options=options)
        
        driver.get(homepage_url)
        time.sleep(2)
        
        try:
            search_box = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "key"))
            )
            search_box.clear()
            search_box.send_keys("LLM")
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
            
        except TimeoutException:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="key"]'))
            )
            search_box.clear()
            search_box.send_keys('LLM')
            search_box.submit()
            time.sleep(3)
        
        # 點選「圖書」分類
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.mod_b, div.searchbook, div.mod"))
        )
        
        book_category = None
        category_selectors = [
            "//label[contains(text(), '圖書') and (contains(text(), '(') or contains(text(), ')'))]",
            "//span[contains(text(), '圖書') and (contains(text(), '(') or contains(text(), ')'))]",
            "//a[contains(text(), '圖書') and (contains(text(), '(') or contains(text(), ')'))]",
            "//input[@value='BKA']/../label",
            "//input[@name='cat' and @value='BKA']/../label",
            "//*[contains(text(), '圖書') and contains(text(), '(')]"
        ]
        
        for selector in category_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        text = element.text.strip()
                        if '圖書' in text and ('(' in text or ')' in text):
                            book_category = element
                            break
                if book_category:
                    break
            except Exception:
                continue
        
        if book_category:
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", book_category)
                time.sleep(1)
                
                try:
                    book_category.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", book_category)
                
                time.sleep(3)
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-searchbox"))
                )
                
            except Exception:
                pass
        
        # 偵測總頁數
        page_count = 1
        try:
            pagination = driver.find_elements(By.CSS_SELECTOR, 'div.mod_pagination a, div.cnt_page a, ul.pagination a, .page_bar a')
            
            if pagination:
                page_numbers = []
                for elem in pagination:
                    text = elem.text.strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                if page_numbers:
                    page_count = max(page_numbers)
            
            if page_count == 1:
                page_text_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '共') and contains(text(), '頁')]")
                for elem in page_text_elements:
                    match = re.search(r'共\s*(\d+)\s*頁', elem.text)
                    if match:
                        page_count = int(match.group(1))
                        break
            
            if page_count == 1:
                result_text = driver.find_elements(By.XPATH, "//*[contains(text(), '搜尋結果共')]")
                for elem in result_text:
                    match = re.search(r'頁數\s*\d+\s*/\s*(\d+)', elem.text)
                    if match:
                        page_count = int(match.group(1))
                        break
                        
        except Exception:
            page_count = 1
        
        print(f"偵測到總共有 {page_count} 頁。")
        
        page_num = 1
        
        while page_num <= page_count:
            print(f"正在爬取第 {page_num} / {page_count} 頁...")
            
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.table-searchbox'))
                )
            except TimeoutException:
                print(f"第 {page_num} 頁載入逾時，跳過。")
                break
            
            page_books = extract_books_from_page(driver)
            books.extend(page_books)
            
            if len(page_books) == 0:
                print("當前頁面沒有書籍資料，停止爬取。")
                break
            
            if page_num >= page_count:
                break
            
            # 嘗試點擊下一頁
            next_button_found = False
            
            next_button_selectors = [
                ("LINK_TEXT", "下一頁"),
                ("PARTIAL_LINK_TEXT", "下一頁"),
                ("XPATH", "//a[text()='下一頁']"),
                ("XPATH", "//a[contains(text(), '下一頁') and not(contains(@class, 'gray'))]"),
                ("XPATH", "//a[contains(@class, 'nxt') and not(contains(@class, 'gray'))]"),
                ("XPATH", "//div[@class='cnt_page']//a[contains(@class, 'nxt')]"),
                ("XPATH", "//ul[@class='pagination']//a[contains(text(), '下一頁')]"),
                ("CSS", "a.nxt:not(.gray)"),
                ("CSS", "div.mod_pagination a:not(.gray)"),
                ("XPATH", "//a[@rel='next']"),
                ("XPATH", f"//a[text()='{page_num + 1}']")
            ]
            
            for selector_type, selector_value in next_button_selectors:
                try:
                    if selector_type == "LINK_TEXT":
                        by_type = By.LINK_TEXT
                    elif selector_type == "PARTIAL_LINK_TEXT":
                        by_type = By.PARTIAL_LINK_TEXT
                    elif selector_type == "XPATH":
                        by_type = By.XPATH
                    elif selector_type == "CSS":
                        by_type = By.CSS_SELECTOR
                    else:
                        continue
                    
                    elements = driver.find_elements(by_type, selector_value)
                    if not elements:
                        continue
                    
                    for next_button in elements:
                        try:
                            if not next_button.is_displayed() or not next_button.is_enabled():
                                continue
                            
                            button_class = next_button.get_attribute('class') or ''
                            if 'gray' in button_class.lower() or 'disabled' in button_class.lower():
                                continue
                            
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                            time.sleep(1)
                            
                            old_url = driver.current_url
                            
                            driver.execute_script("arguments[0].click();", next_button)
                            
                            time.sleep(3)
                            new_url = driver.current_url
                            
                            if old_url != new_url:
                                next_button_found = True
                                time.sleep(2)
                                page_num += 1
                                break
                                
                        except Exception:
                            continue
                    
                    if next_button_found:
                        break
                    
                except Exception:
                    continue
            
            if not next_button_found:
                break
        
        print("爬取完成。")
        
    except Exception as e:
        print(f"爬蟲錯誤：{e}")
        raise
    
    finally:
        try:
            driver.quit()
        except Exception:
            pass
    
    return books


def extract_books_from_page(driver: webdriver.Chrome) -> List[Dict[str, Any]]:
    """
    從當前頁面擷取所有書籍資料。
    
    技術細節：
    1. 資料擷取：程式需能正確抓取每一本書的上述四個欄位
    2. 提示 1：所有書籍資訊都包含在 div.table-searchbox 區域中，
              每一本書是一個 div.table-td 元素
    3. 提示 2：書名和連結在 <h4> 標籤內的 <a> 標籤中，
              作者資訊在 <p class="author"> 下的 <a> 標籤中，
              可能有多位作者，請將所有作者名稱合併成一個字串
    4. 資料清理：價格欄位可能包含非數字字元，如「優惠價：<b>79</b> 折，<b>513</b> 元」。
              您必須從中僅擷取出數字 513 並轉換為整數
    5. 強固處理：若書籍缺少作者或價格資訊，爬蟲應能優雅地處理這種情況（例如，存入 N/A 或預設值 0），
              而不是直接崩潰
    
    參數:
        driver: Selenium WebDriver 實例
    
    回傳:
        List[Dict[str, Any]]: 當前頁面的書籍資料列表
    """
    books = []
    
    try:
        book_containers = driver.find_elements(By.CSS_SELECTOR, 'div.table-searchbox div.table-td')
        
        for container in book_containers:
            try:
                title_elems = container.find_elements(By.CSS_SELECTOR, 'h4 a')
                if not title_elems:
                    continue
                
                title_elem = title_elems[0]
                title = title_elem.text.strip()
                link = title_elem.get_attribute('href')
                
                # 擷取作者
                author = 'N/A'
                try:
                    author_elems = container.find_elements(By.CSS_SELECTOR, 'p.author a')
                    if author_elems:
                        authors = [elem.text.strip() for elem in author_elems if elem.text.strip()]
                        if authors:
                            author = ', '.join(authors)
                except NoSuchElementException:
                    pass
                except Exception:
                    pass
                
                # 擷取價格
                price = 0
                try:
                    price_container = container.find_elements(By.CSS_SELECTOR, 'p.price, li.price_a, div.price')
                    
                    if price_container:
                        price_text = price_container[0].text
                        match = re.search(r'(\d+)\s*元', price_text)
                        if match:
                            price = int(match.group(1))
                        else:
                            numbers = re.findall(r'\d+', price_text)
                            if numbers:
                                large_numbers = [int(n) for n in numbers if int(n) >= 100]
                                if large_numbers:
                                    price = max(large_numbers)
                    
                    if price == 0:
                        full_text = container.text
                        match = re.search(r'(\d+)\s*元', full_text)
                        if match:
                            price = int(match.group(1))
                    
                except (NoSuchElementException, ValueError):
                    pass
                except Exception:
                    pass
                
                if title and link:
                    book = {
                        'title': title,
                        'author': author,
                        'price': price,
                        'link': link
                    }
                    books.append(book)
                    
            except Exception:
                continue
    
    except Exception as e:
        print(f"擷取頁面資料時發生錯誤：{e}")
    
    return books


if __name__ == '__main__':
    # 測試爬蟲功能
    print("開始測試爬蟲...")
    books = scrape_books()
    print(f"\n共爬取 {len(books)} 筆書籍資料")
    
    # 顯示前 3 筆資料
    for i, book in enumerate(books[:3], 1):
        print(f"\n第 {i} 本書：")
        print(f"  書名：{book['title']}")
        print(f"  作者：{book['author']}")
        print(f"  價格：{book['price']}")
        print(f"  連結：{book['link']}")

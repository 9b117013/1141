"""
博客來 LLM 書籍管理系統 - 主程式
"""

from typing import Optional
import database
import scraper


def show_main_menu() -> None:
    """顯示主選單。"""
    print("\n----- 博客來 LLM 書籍管理系統 -----")
    print("1. 更新書籍資料庫")
    print("2. 查詢書籍")
    print("3. 離開系統")
    print("---------------------------------")


def show_search_menu() -> None:
    """顯示查詢子選單。"""
    print("\n--- 查詢書籍 ---")
    print("a. 依書名查詢")
    print("b. 依作者查詢")
    print("c. 返回主選單")
    print("---------------")


def update_database() -> None:
    """
    更新書籍資料庫。
    
    爬取博客來網站的最新書籍資料，並將資料存入資料庫。
    """
    try:
        print("開始從網路爬取最新書籍資料...")
        
        books = scraper.scrape_books()
        total_scraped = len(books)
        
        inserted_count = database.insert_books(books)
        
        print(f"資料庫更新完成！共爬取 {total_scraped} 筆資料，新增了 {inserted_count} 筆新書記錄。")
        
    except Exception as e:
        print(f"更新資料庫時發生錯誤：{e}")





def search_books() -> None:
    """
    查詢書籍功能。
    
    提供子選單讓使用者選擇查詢方式（書名或作者）。
    """
    while True:
        show_search_menu()
        choice = input("請選擇查詢方式 (a-c): ").strip().lower()
        
        if choice == 'a':
            keyword = input("請輸入關鍵字: ").strip()
            try:
                results = database.search_by_title(keyword)
                display_search_results(results)
            except Exception as e:
                print(f"查詢時發生錯誤：{e}")
        
        elif choice == 'b':
            keyword = input("請輸入關鍵字: ").strip()
            try:
                results = database.search_by_author(keyword)
                display_search_results(results)
            except Exception as e:
                print(f"查詢時發生錯誤：{e}")
        
        elif choice == 'c':
            break
        
        else:
            print("無效選項，請重新輸入。")


def display_search_results(results: list) -> None:
    """
    顯示查詢結果。
    
    參數:
        results: 查詢結果列表
    """
    if not results:
        print("\n查無資料。")
    else:
        print(f"\n{'=' * 80}")
        for row in results:
            print(f"書名：{row['title']}")
            print(f"作者：{row['author']}")
            print(f"價格：{row['price']}")
            print(f"{'-' * 80}")
        print(f"{'=' * 80}")


def main() -> None:
    """主程式進入點。"""
    try:
        database.init_database()
    except Exception as e:
        print(f"資料庫初始化失敗：{e}")
        return
    
    while True:
        show_main_menu()
        choice = input("請選擇操作選項 (1-3): ").strip()
        
        if choice == '1':
            update_database()
        
        elif choice == '2':
            search_books()
        
        elif choice == '3':
            print("\n感謝使用，系統已退出。")
            break
        
        else:
            print("\n無效選項，請重新輸入。")


if __name__ == '__main__':
    main()


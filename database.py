"""
資料庫管理模組
"""

import sqlite3
from typing import List, Dict, Any, Optional


def init_database() -> None:
    """
    初始化資料庫，建立 llm_books 資料表。
    
    若資料表已存在則不會重複建立。
    資料表結構：
    - id: INTEGER (主鍵，自動遞增)
    - title: TEXT (不可為空，唯一)
    - author: TEXT
    - price: INTEGER
    - link: TEXT
    """
    try:
        with sqlite3.connect('books.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS llm_books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    author TEXT,
                    price INTEGER,
                    link TEXT
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"資料庫初始化錯誤：{e}")
        raise


def insert_books(books: List[Dict[str, Any]]) -> int:
    """
    批量插入書籍資料到資料庫。
    
    使用 INSERT OR IGNORE 語法，若書名已存在則自動忽略。
    
    參數:
        books: 書籍資料列表，每個元素為字典，包含 title, author, price, link
    
    回傳:
        int: 成功新增的書籍數量
    """
    if not books:
        return 0
    
    try:
        with sqlite3.connect('books.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM llm_books')
            count_before = cursor.fetchone()[0]
            
            for book in books:
                cursor.execute('''
                    INSERT OR IGNORE INTO llm_books (title, author, price, link)
                    VALUES (?, ?, ?, ?)
                ''', (book['title'], book['author'], book['price'], book['link']))
            
            conn.commit()
            
            cursor.execute('SELECT COUNT(*) FROM llm_books')
            count_after = cursor.fetchone()[0]
            
            inserted_count = count_after - count_before
            
            return inserted_count
            
    except sqlite3.Error as e:
        print(f"資料插入錯誤：{e}")
        raise


def search_by_title(keyword: str) -> List[sqlite3.Row]:
    """
    依書名關鍵字搜尋書籍（模糊比對）。
    
    參數:
        keyword: 搜尋關鍵字
    
    回傳:
        List[sqlite3.Row]: 符合條件的書籍列表
    """
    try:
        with sqlite3.connect('books.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT title, author, price FROM llm_books
                WHERE title LIKE ?
                ORDER BY title
            ''', (f'%{keyword}%',))
            
            results = cursor.fetchall()
            return results
            
    except sqlite3.Error as e:
        print(f"查詢錯誤：{e}")
        raise


def search_by_author(keyword: str) -> List[sqlite3.Row]:
    """
    依作者關鍵字搜尋書籍（模糊比對）。
    
    參數:
        keyword: 搜尋關鍵字
    
    回傳:
        List[sqlite3.Row]: 符合條件的書籍列表
    """
    try:
        with sqlite3.connect('books.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT title, author, price FROM llm_books
                WHERE author LIKE ?
                ORDER BY title
            ''', (f'%{keyword}%',))
            
            results = cursor.fetchall()
            return results
            
    except sqlite3.Error as e:
        print(f"查詢錯誤：{e}")
        raise





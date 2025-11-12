# 博客來 LLM 書籍管理系統

整合 Selenium 網頁爬蟲與 SQLite 資料庫的 Python 應用程式，自動化地從博客來網路書店爬取「LLM」相關書籍資料，並提供命令列介面查詢書籍資訊。

## 功能特色

- **自動化網頁爬蟲**：使用 Selenium 模擬使用者操作，從博客來爬取所有分頁的書籍資料
- **資料庫管理**：使用 SQLite 儲存書籍，自動避免重複資料（UNIQUE + INSERT OR IGNORE）
- **書籍查詢**：支援書名和作者的模糊查詢（LIKE '%keyword%'）

## 系統需求

- Python 3.8 或以上版本
- Chrome 瀏覽器
- ChromeDriver（需與 Chrome 版本相容）

## 安裝步驟

1. 安裝所需套件：
```bash
pip install -r requirements.txt
```

2. 確認已安裝 Chrome 瀏覽器。

## 使用方法

執行主程式：

```bash
python app.py
```

### 主選單功能

1. **更新書籍資料庫**：爬取博客來網站的 LLM 書籍資料並存入資料庫
2. **查詢書籍**：依書名或作者進行模糊查詢
3. **離開系統**

## 專案結構

```
.
├── app.py              # 主程式與使用者介面
├── scraper.py          # 網頁爬蟲模組
├── database.py         # 資料庫管理模組
├── requirements.txt    # Python 套件相依性
├── README.md          # 專案說明文件
├── LICENSE            # 授權條款
├── .gitignore         # Git 忽略檔案設定
├── .gitattributes     # Git 屬性設定
└── books.db           # SQLite 資料庫檔案（執行後自動產生）
```

## 資料庫結構

### llm_books 資料表

| 欄位名稱 | 資料型別 | 說明 |
|---------|---------|------|
| id | INTEGER | 主鍵，自動遞增 |
| title | TEXT | 書名（唯一） |
| author | TEXT | 作者 |
| price | INTEGER | 價格 |
| link | TEXT | 書籍連結 |

## 技術特點


**scraper.py (網頁爬蟲)**
- Selenium WebDriver：自動化瀏覽器操作
- WebDriverWait：等待頁面元素載入
- 正則表達式：清理價格資料（提取「513 元」中的數字）

**database.py (資料庫管理)**
- SQLite3：輕量級資料庫
- `with` 語句：自動管理連線
- `INSERT OR IGNORE`：避免重複資料
- `LIKE '%keyword%'`：模糊查詢

**app.py (使用者介面)**
- 命令列介面 (CLI)
- 模組整合：呼叫 scraper 和 database
- 完善的例外處理

### 程式碼品質

- 符合 PEP8 編碼風格
- 100% 型別提示（Type Hints）
- 完整的 Docstrings
- 模組化設計

## 授權條款

本專案採用 MIT 授權條款。

## 作者

期中專案作業 


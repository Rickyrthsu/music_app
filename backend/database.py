import sqlite3
import datetime
import os

# 設定資料庫檔案的路徑 (會放在 backend 資料夾內)
DB_PATH = os.path.join(os.path.dirname(__file__), 'lumiya.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 讓我們可以用欄位名稱存取資料
    return conn

def init_db():
    """ 初始化資料庫：如果沒有資料表就建立一個 """
    conn = get_db_connection()
    # 建立 mood_logs 資料表
    # 欄位：ID, 日期, 使用者日記, AI分析的情緒關鍵字, 推薦歌名, Spotify連結
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_text TEXT NOT NULL,
            mood_keyword TEXT,
            song_name TEXT,
            artist_name TEXT,
            spotify_url TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ 資料庫 (SQLite) 初始化完成")

def save_log(user_text, mood_keyword, song_name, artist_name, spotify_url):
    """ 儲存一筆新的日記與推薦結果 """
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO mood_logs (user_text, mood_keyword, song_name, artist_name, spotify_url) VALUES (?, ?, ?, ?, ?)',
            (user_text, mood_keyword, song_name, artist_name, spotify_url)
        )
        conn.commit()
        conn.close()
        print(f"💾 已儲存日記紀錄: {user_text[:10]}...")
        return True
    except Exception as e:
        print(f"❌ 儲存失敗: {e}")
        return False

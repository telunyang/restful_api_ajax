import sqlite3
import pandas as pd

# 資料庫檔案名稱
DB_PATH = "my_db.db"

# CSV 檔案路徑
CSV_PATH = "titanic.csv"

# 建立資料表的 SQL 語句，包含欄位定義和約束條件
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS titanic (
    PassengerId INTEGER PRIMARY KEY,
    Survived INTEGER NOT NULL CHECK (Survived IN (0, 1)),
    Pclass INTEGER NOT NULL CHECK (Pclass IN (1, 2, 3)),
    Name TEXT NOT NULL CHECK (length(Name) <= 100),
    Sex TEXT NOT NULL CHECK (Sex IN ('male', 'female')),
    Age REAL CHECK (Age IS NULL OR (Age >= 0 AND Age <= 120)),
    SibSp INTEGER NOT NULL DEFAULT 0 CHECK (SibSp >= 0),
    Parch INTEGER NOT NULL DEFAULT 0 CHECK (Parch >= 0),
    Ticket TEXT NOT NULL CHECK (length(Ticket) <= 30),
    Fare REAL NOT NULL DEFAULT 0 CHECK (Fare >= 0),
    Cabin TEXT CHECK (Cabin IS NULL OR length(Cabin) <= 30),
    Embarked TEXT CHECK (Embarked IS NULL OR Embarked IN ('C', 'Q', 'S'))
);
"""

# 建立索引的 SQL 語句，提升查詢效率
CREATE_INDEX_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_titanic_survived ON titanic(Survived);",
    "CREATE INDEX IF NOT EXISTS idx_titanic_pclass ON titanic(Pclass);",
    "CREATE INDEX IF NOT EXISTS idx_titanic_name ON titanic(Name);"
]

# 初始化資料庫，建立資料表並匯入 CSV 資料
def init_db():
    # 連接到 SQLite 資料庫，如果資料庫不存在會自動建立
    conn = sqlite3.connect(DB_PATH)

    try:
        # 建立游標物件，用於執行 SQL 語句
        cursor = conn.cursor()

        # 如果資料表已存在，先刪除再重新建立，以確保資料表結構正確
        cursor.execute("DROP TABLE IF EXISTS titanic;")
        cursor.execute(CREATE_TABLE_SQL)

        # 建立索引，提升查詢效率
        for sql in CREATE_INDEX_SQL:
            cursor.execute(sql)

        # 使用 pandas 讀取 CSV 檔案，並將資料匯入 SQLite 資料庫
        df = pd.read_csv(CSV_PATH)

        # pandas 的 NaN 需要轉成 None，SQLite 才會存成 NULL
        df = df.where(pd.notnull(df), None)

        # 將 DataFrame 的資料匯入 SQLite 資料庫的 titanic 資料表
        df.to_sql("titanic", conn, if_exists="append", index=False)

        # 提交事務，將所有變更儲存到資料庫
        conn.commit()
    except sqlite3.Error as e:
        # 發生錯誤時回滾事務，確保資料庫不會處於不一致的狀態
        conn.rollback()
        print(f"資料庫初始化失敗: {e}")
    finally:
        # 關閉資料庫連接，釋放資源
        conn.close()
        print("my_db.db 建立完成，titanic 資料表已匯入。")


if __name__ == "__main__":
    init_db()

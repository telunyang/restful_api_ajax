import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# ============================================================
# 1. 全域讀取資料庫
# ============================================================

DATABASE = "my_db.db"

# 這裡我們直接在全域讀取資料庫，這樣在每個 route 就可以直接使用 db 來存取資料庫了。
db = sqlite3.connect(DATABASE, check_same_thread=False)

# 讓我們在讀取資料庫時，可以直接用 row["欄位名稱"] 的方式來存取資料，
# 而不是 row[0]、row[1] 這樣的 index。
db.row_factory = sqlite3.Row


# ============================================================
# 2. 小工具：把 SQLite Row 轉成 dict
# ============================================================

def row_to_dict(row):
    return dict(row)


# ============================================================
# 3. 前端頁面 Routes
# ============================================================

# 首頁
@app.route("/")
def index_page():
    return render_template("index.html")

# 新增乘客頁面
@app.route("/passengers/new")
def new_passenger_page():
    return render_template("new.html")

# 編輯乘客頁面
@app.route("/passengers/<int:passenger_id>/edit")
def edit_passenger_page(passenger_id):
    return render_template("edit.html", passenger_id=passenger_id)


# ============================================================
# 4. API：取得全部乘客資料，包含簡單分頁
# GET /api/passengers?page=1&per_page=20
# ============================================================

@app.route("/api/passengers", methods=["GET"])
def get_passengers():
    # 讀取 query string 的 page 和 per_page 參數，並設定預設值
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # 搜尋姓名
    search = request.args.get("search", "")

    # 計算 SQL 查詢的 offset，用於分頁
    offset = (page - 1) * per_page

    # 根據是否有搜尋關鍵字，執行不同的 SQL 查詢
    if search != "":
        # 有輸入搜尋關鍵字：只查詢姓名符合的資料
        total_row = db.execute(
            """
            SELECT COUNT(*) AS total
            FROM titanic
            WHERE Name LIKE ?
            """,
            (f"%{search}%",)
        ).fetchone()

        rows = db.execute(
            """
            SELECT *
            FROM titanic
            WHERE Name LIKE ?
            ORDER BY PassengerId
            LIMIT ?
            OFFSET ?
            """,
            (f"%{search}%", per_page, offset)
        ).fetchall()

    else:
        # 沒有輸入搜尋關鍵字：查詢全部資料
        total_row = db.execute(
            """
            SELECT COUNT(*) AS total
            FROM titanic
            """
        ).fetchone()

        # 根據 page 和 per_page 的值，從資料庫查詢對應的資料列，
        # 並按照 PassengerId 排序。
        rows = db.execute(
            """
            SELECT *
            FROM titanic
            ORDER BY PassengerId
            LIMIT ?
            OFFSET ?
            """,
            (per_page, offset)
        ).fetchall()

    # 總共有多少筆資料
    total = total_row["total"]

    # 最後回傳 JSON 格式的資料，包含 items（資料列表）、page、per_page 和 total。
    return jsonify({
        "message": "ok",
        "items": [row_to_dict(row) for row in rows],
        "page": page,
        "per_page": per_page,
        "total": total
    }), 200


# ============================================================
# 5. API：取得單一乘客
# GET /api/passengers/1
# ============================================================

@app.route("/api/passengers/<int:passenger_id>", methods=["GET"])
def get_passenger(passenger_id):
    # 根據 passenger_id 查詢資料庫，看看有沒有這個乘客的資料。
    row = db.execute(
        "SELECT * FROM titanic WHERE PassengerId = ?",
        (passenger_id,)
    ).fetchone()

    # 如果 row 是 None，代表資料庫裡沒有這個 passenger_id 的資料，我們就回傳 404 Not Found 的錯誤訊息。
    if row is None:
        return jsonify({"error": "找不到資料"}), 404

    # 如果有找到資料，我們就把這筆資料轉成 dict，然後回傳 JSON 格式的資料。
    return jsonify({
        "message": "ok", 
        "item": row_to_dict(row)}
    ), 200


# ============================================================
# 6. API：新增乘客
# POST /api/passengers
# ============================================================

@app.route("/api/passengers", methods=["POST"])
def create_passenger():
    # 從 request 的 JSON body 讀取資料
    data = request.get_json()

    # 執行 SQL INSERT 語句，把新的乘客資料新增到 titanic 資料表中。
    cursor = db.execute(
        """
        INSERT INTO titanic (
            Survived, Pclass, Name, Sex, Age,
            SibSp, Parch, Ticket, Fare, Cabin,
            Embarked
        )
        VALUES (
            ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, 
            ?
        )
        """,
        (
            data["Survived"],
            data["Pclass"],
            data["Name"],
            data["Sex"],
            data["Age"],
            data["SibSp"],
            data["Parch"],
            data["Ticket"],
            data["Fare"],
            data["Cabin"],
            data["Embarked"]
        )
    )

    # 執行 commit()，把剛剛的 INSERT 操作真正寫入資料庫。
    db.commit()

    # cursor.lastrowid 會回傳剛剛 INSERT 的那筆資料的自動增加的 ID，
    # 也就是 PassengerId。
    new_id = cursor.lastrowid

    # 根據 new_id 查詢剛剛新增的那筆資料，這樣我們就可以把完整的資料回傳給前端了。
    row = db.execute(
        "SELECT * FROM titanic WHERE PassengerId = ?",
        (new_id,)
    ).fetchone()

    # 最後回傳 JSON 格式的資料，包含 message 和 item（剛剛新增的那筆資料）。
    return jsonify({
        "message": "created",
        "item": row_to_dict(row)
    }), 201


# ============================================================
# 7. API：修改乘客
# PUT /api/passengers/1
# ============================================================

@app.route("/api/passengers/<int:passenger_id>", methods=["PUT"])
def update_passenger(passenger_id):
    # 從 request 的 JSON body 讀取資料
    data = request.get_json()

    # 執行 SQL UPDATE 語句，根據 passenger_id 把對應的資料更新成新的值。
    cursor = db.execute(
        """
        UPDATE titanic
        SET
            Survived = ?,
            Pclass = ?,
            Name = ?,
            Sex = ?,
            Age = ?,
            SibSp = ?,
            Parch = ?,
            Ticket = ?,
            Fare = ?,
            Cabin = ?,
            Embarked = ?
        WHERE PassengerId = ?
        """,
        (
            data["Survived"],
            data["Pclass"],
            data["Name"],
            data["Sex"],
            data["Age"],
            data["SibSp"],
            data["Parch"],
            data["Ticket"],
            data["Fare"],
            data["Cabin"],
            data["Embarked"],
            passenger_id
        )
    )

    # 執行 commit()，把剛剛的 UPDATE 操作真正寫入資料庫。
    db.commit()

    # 如果沒有更新任何資料，則回傳 404 Not Found 的錯誤訊息。
    if cursor.rowcount == 0:
        return jsonify({"error": "找不到資料"}), 404

    # 根據 passenger_id 查詢剛剛更新的那筆資料，這樣我們就可以把完整的資料回傳給前端了。
    row = db.execute(
        "SELECT * FROM titanic WHERE PassengerId = ?",
        (passenger_id,)
    ).fetchone()

    # 如果 row 是 None，代表資料庫裡沒有這個 passenger_id 的資料，我們就回傳 404 Not Found 的錯誤訊息。
    if row is None:
        return jsonify({"error": "找不到資料"}), 404

    # 最後回傳 JSON 格式的資料，包含 message 和 item（剛剛更新的那筆資料）。
    return jsonify({
        "message": "updated",
        "item": row_to_dict(row)
    }), 200


# ============================================================
# 8. API：刪除乘客
# DELETE /api/passengers/1
# ============================================================

@app.route("/api/passengers/<int:passenger_id>", methods=["DELETE"])
def delete_passenger(passenger_id):
    # 執行 SQL DELETE 語句，根據 passenger_id 把對應的資料從 titanic 資料表中刪除。
    cursor = db.execute(
        "DELETE FROM titanic WHERE PassengerId = ?",
        (passenger_id,)
    )

    # 執行 commit()，把剛剛的 DELETE 操作真正寫入資料庫。
    db.commit()

    # 如果沒有刪除任何資料，則回傳 404 Not Found 的錯誤訊息。
    if cursor.rowcount == 0:
        return jsonify({"error": "找不到資料"}), 404

    # 最後回傳 JSON 格式的資料，包含 message，告訴前端這筆資料已經被刪除了。
    return jsonify({
        "message": "deleted"
    }), 200 # 你也可以設定 204，但不會有 response body，前端無法判斷成功還是失敗


# ============================================================
# 9. 啟動 Flask
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
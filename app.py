from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_NAME = "cases.db"

# -------------------------
# DATABASE CONNECTION (OPTIMIZED)
# -------------------------
def get_db_connection():
    conn = sqlite3.connect(
        DB_NAME,
        timeout=10,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")  # performance boost
    return conn


# -------------------------
# INITIALIZE DATABASE
# -------------------------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caseType TEXT NOT NULL,
            plaintiff TEXT NOT NULL,
            defendant TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)
    conn.commit()
    conn.close()

init_db()


# -------------------------
# SUBMIT CASE
# -------------------------
@app.route("/cases", methods=["POST"])
def submit_case():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["caseType", "plaintiff", "defendant", "description"]
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"{field} is required"}), 400

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO cases (caseType, plaintiff, defendant, description)
        VALUES (?, ?, ?, ?)
    """, (
        data["caseType"],
        data["plaintiff"],
        data["defendant"],
        data["description"]
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Case stored successfully"}), 201


# -------------------------
# GET ALL CASES
# -------------------------
@app.route("/cases", methods=["GET"])
def get_cases():
    conn = get_db_connection()
    cases = conn.execute(
        "SELECT * FROM cases ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return jsonify([dict(case) for case in cases])


# -------------------------
# GET CASE BY ID
# -------------------------
@app.route("/cases/<int:case_id>", methods=["GET"])
def get_case(case_id):
    conn = get_db_connection()
    case = conn.execute(
        "SELECT * FROM cases WHERE id = ?", (case_id,)
    ).fetchone()
    conn.close()

    if case is None:
        return jsonify({"error": "Case not found"}), 404

    return jsonify(dict(case))


# -------------------------
# RUN SERVER (NO RELOAD BUG)
# -------------------------
if __name__ == "__main__":
    app.run(port=5000, threaded=True)

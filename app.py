from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # allow cross-origin requests

DB = "rent.db"

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tenants(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flat TEXT,
            name TEXT,
            phone TEXT,
            nid TEXT,
            father TEXT,
            mother TEXT,
            address TEXT,
            month TEXT,
            rent REAL,
            paid REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Add tenant (All months)
@app.route("/add", methods=["POST"])
def add_tenant():
    data = request.json
    months = data.get("months", [])
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    for month in months:
        c.execute('''INSERT INTO tenants(flat,name,phone,nid,father,mother,address,month,rent,paid)
                     VALUES (?,?,?,?,?,?,?,?,?,?)''',
                  (data["flat"], data["name"], data["phone"], data["nid"],
                   data["father"], data["mother"], data["address"], month, data["rent"], 0))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# Get tenants by month
@app.route("/tenants/<month>", methods=["GET"])
def get_tenants(month):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM tenants WHERE month=?", (month,))
    rows = c.fetchall()
    columns = [col[0] for col in c.description]
    data = [dict(zip(columns,row)) for row in rows]
    conn.close()
    return jsonify(data)

# Update paid amount
@app.route("/pay/<int:id>", methods=["PATCH"])
def pay(id):
    amount = request.json.get("paid",0)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Add to existing paid
    c.execute("UPDATE tenants SET paid=paid+? WHERE id=?", (amount,id))
    conn.commit()
    conn.close()
    return jsonify({"status":"success"})

# Delete tenant (current month)
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM tenants WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status":"success"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, jsonify
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            balance INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    conn.commit()
    conn.close()




app = Flask(__name__)

# temporary in-memory storage


@app.route("/", methods=["GET"])
def home():
    return "Banking API is running"

@app.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json()

    name= data.get("name")
    email=data.get("email")

    if not name or not email:
        return jsonify({
            "error": "name and email are required"
        }), 400

    conn=get_db_connection()
    cursor= conn.cursor()

    existing = cursor.execute(
        "SELECT * FROM customers WHERE email= ?",
        (email,)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({
            "error": "Customer already exists"
        }), 409

    cursor.execute(
        "INSERT INTO customers (name, email) VALUES (?, ?)",
        (data.get("name"), data.get("email"))
    )

    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": customer_id,
        "name": data.get("name"),
        "email": data.get("email")
    }), 201

@app.route("/customers", methods=["GET"])
def get_customers():
    conn=get_db_connection()
    customers=conn.execute("SELECT * FROM customers").fetchall()
    conn.close()

    return jsonify([dict(c) for c in customers]), 200

@app.route("/accounts", methods=["POST"])
def create_account():
    data=request.get_json()
    customer_id= data.get("customer_id")

    conn=get_db_connection()
    cursor = conn.cursor()

    customer = cursor.execute("Select * FROM customers WHERE id= ?",
                              (customer_id,)).fetchone()
    
    if not customer:
        conn.close()
        return jsonify({"error": "Customer not found"}), 404
    
    cursor.execute(
        "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)", (customer_id, 0)
    )

    conn.commit()
    account_id=cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Account created succesfully",
        "account": {
        "account_id": account_id,
        "customer_id": customer_id,
        "balance": 0
        }
    }), 201


@app.route("/deposits", methods=["POST"])
def deposit():
    data=request.get_json()
    account_id=data.get("account_id")
    amount=data.get("amount")

    

    conn= get_db_connection()
    cursor= conn.cursor()

    if amount is None or amount<=0:
        conn.close()
        return jsonify({
            "error": "Amount must be greater than 0"
        }), 400

    account= cursor.execute(
        "SELECT * FROM accounts WHERE account_id=?", 
        (account_id,)).fetchone()
    
    if not account:
        conn.close()
        return jsonify({
            "error": "Account does not exists"
        }), 404
    
    new_balance=account["balance"]+amount
    
    cursor.execute(
        "UPDATE accounts SET balance =? WHERE account_id=?", (new_balance, account_id)

    )

    conn.commit()
    conn.close()

    return jsonify ({
        "message": "Deposit succesful",
        "balance": new_balance
    }), 200


@app.route("/withdraw", methods=["POST"])
def withdraw():
    data=request.get_json()
    account_id=data.get("account_id")
    amount=data.get("amount")

    conn= get_db_connection()
    cursor= conn.cursor()

    if amount is None or amount<=0:
        conn.close()
        return jsonify({
            "error": "Amount must be greater than 0"
        }), 400

    account= cursor.execute(
        "SELECT * FROM accounts WHERE account_id = ?",
        (account_id,)
    ).fetchone()

    if not account:
        conn.close()
        return jsonify ({
            "error": "Account not found"
        }),404
    
    if account["balance"]< amount:
        conn.close()
        return jsonify ({
            "error": "Insufficeinet balance"
        }), 400
    
    new_balance = account["balance"] - amount

    cursor.execute(
        "UPDATE accounts SET balance = ? WHERE account_id =?",
        (new_balance, account_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Withdrawal succesful",
        "balance": new_balance
    }), 200

@app.route("/balance/<int:account_id>", methods=["GET"])
def get_balance(account_id):
    conn=get_db_connection()
    account = conn.execute(
        "SELECT * FROM accounts WHERE account_id = ?",
        (account_id,)
    ). fetchone()
    conn.close()

    if not account:
        return jsonify({
            "error": "Account not found"
        }), 404
    
    return jsonify({
        "account_id": account_id,
        "balance": account["balance"]
    }), 200


    

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

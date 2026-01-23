from flask import Blueprint, request, jsonify
from db import get_db_connection

accounts_bp = Blueprint("accounts", __name__)

@accounts_bp.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json()
    customer_id = data.get("customer_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    customer = cursor.execute(
        "SELECT * FROM customers WHERE id = ?",
        (customer_id,)
    ).fetchone()

    if not customer:
        conn.close()
        return jsonify({"error": "Customer not found"}), 404

    cursor.execute(
        "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)",
        (customer_id, 0)
    )

    conn.commit()
    account_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "account_id": account_id,
        "customer_id": customer_id,
        "balance": 0
    }), 201

@accounts_bp.route("/deposit", methods=["POST"])
def deposit():
    data = request.get_json()
    account_id = data.get("account_id")
    amount = data.get("amount")

    if amount is None or amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    account = cursor.execute(
        "SELECT * FROM accounts WHERE account_id = ?",
        (account_id,)
    ).fetchone()

    if not account:
        conn.close()
        return jsonify({"error": "Account not found"}), 404

    new_balance = account["balance"] + amount

    

    cursor.execute(
        "UPDATE accounts SET balance = ? WHERE account_id = ?",
        (new_balance, account_id)
    )

    cursor.execute(
        "INSERT INTO transactions (account_id, type, amount) VALUES (?,?,?)",
        (account_id, "deposit", amount)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Deposit successful",
        "balance": new_balance
    }), 200


@accounts_bp.route("/withdraw", methods=["POST"])
def withdraw():
    data = request.get_json()
    account_id = data.get("account_id")
    amount = data.get("amount")

    if amount is None or amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    account = cursor.execute(
        "SELECT * FROM accounts WHERE account_id = ?",
        (account_id,)
    ).fetchone()

    if not account:
        conn.close()
        return jsonify({"error": "Account not found"}), 404

    if account["balance"] < amount:
        conn.close()
        return jsonify({"error": "Insufficient balance"}), 400

    new_balance = account["balance"] - amount

    cursor.execute(
        "UPDATE accounts SET balance = ? WHERE account_id = ?",
        (new_balance, account_id)
    )
    cursor.execute(
    "INSERT INTO transactions (account_id, type, amount) VALUES (?, ?, ?)",
    (account_id, "withdraw", amount)
)

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Withdrawal successful",
        "balance": new_balance
    }), 200

@accounts_bp.route("/accounts/<int:account_id>/transactions", methods=["GET"])
def get_transactions(account_id):
    conn= get_db_connection()

    transactions= conn.execute(
        "SELECT * FROM transactions WHERE account_id = ? ORDER BY timestamp DESC",
        (account_id, )
    ).fetchall()

    conn.close()

    return jsonify([dict(t) for t in transactions]), 200



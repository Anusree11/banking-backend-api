from flask import Blueprint, request, jsonify
from db import get_db_connection

customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT * FROM customers WHERE email = ?",
        (email,)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({"error": "Customer already exists"}), 409

    cursor.execute(
        "INSERT INTO customers (name, email) VALUES (?, ?)",
        (name, email)
    )

    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": customer_id,
        "name": name,
        "email": email
    }), 201


@customers_bp.route("/customers", methods=["GET"])
def get_customers():
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers").fetchall()
    conn.close()

    return jsonify([dict(c) for c in customers]), 200

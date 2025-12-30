from flask import Flask, request, jsonify
import sqlite3



app = Flask(__name__)

# temporary in-memory storage
customers = []
accounts = []

@app.route("/", methods=["GET"])
def home():
    return "Banking API is running"

@app.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json()

    customer = {
        "id": len(customers) + 1,
        "name": data.get("name"),
        "email": data.get("email")
    }

    customers.append(customer)

    return jsonify({
        "message": "Customer created successfully",
        "customer": customer
    }), 201

@app.route("/customers", methods=["GET"])
def get_customers():
    return jsonify(customers), 200

@app.route("/accounts", methods=["POST"])
def create_account():
    data=request.get_json()
    customer_id= data.get("customer_id")

    customer_exists = any(c["id"]== customer_id for c in customers)
    
    if not customer_exists:
        return jsonify({"error": "Customer not found"}), 404
    
    account = {
        "account_id": len(accounts) + 1,
        "customer_id": customer_id,
        "balance":0
    }

    accounts.append(account)

    return jsonify({
        "message": "Account created successfully",
        "account": account
    }), 201

@app.route("/deposits", methods=["POST"])
def deposit():
    data=request.get_json()
    account_id=data.get("account_id")
    amount=data.get("amount")

    for account in accounts:
        if account["account_id"] == account_id:
            account["balance"]+=amount

            return jsonify ({
                "message": "Deposit succesfully",
                "balance": account["balance"]
            }), 200
        
    return jsonify ({"error": "Account not found"}), 404

@app.route("/withdraw", methods=["POST"])
def withdraw():
    data=request.get_json()
    account_id=data.get("account_id")
    amount=data.get("amount")

    for account in accounts:
        if account["account_id"]==account_id:
            if account["balance"] < amount:
                return jsonify ({"error": "Insufficient balance"}), 400
            
            account["balance"]-=amount

            return jsonify ({
                "message": "Withdrawel Succesful",
                "balance": account["balance"]
            }), 200

if __name__ == "__main__":
    
    app.run(debug=True)

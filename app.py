from flask import Flask
from db import init_db
from routes.customers import customers_bp
from routes.accounts import accounts_bp

app = Flask(__name__)

app.register_blueprint(customers_bp)
app.register_blueprint(accounts_bp)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

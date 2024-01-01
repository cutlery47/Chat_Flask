from flask import Flask
from blueprints.Users.routes import users_bp
from blueprints.Auth.routes import auth_bp

app = Flask(__name__)

# ==================BLUEPRINTS======================
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True)

# TODO: 1) AUTH, 2) permissions
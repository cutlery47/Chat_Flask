from flask import Flask
from blueprints.Users.routes import users_bp
from blueprints.Auth.routes import auth_bp
from blueprints.Chats.routes import chats_bp

app = Flask(__name__)

# ==================BLUEPRINTS======================
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(chats_bp, url_prefix="/chats")

if __name__ == "__main__":
    app.run(debug=True)

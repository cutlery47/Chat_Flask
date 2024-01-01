from flask import make_response
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flaskr.settings import Settings
import jwt


from flaskr.blueprints.Users.views import findUserByUsername

def authLogInView(request):
    # check if both username and password are provided
    try:
        username = request.form['username']
        password = request.form['password']
    except KeyError:
        return make_response("Error: Bad request data!", 400)

    user = findUserByUsername(username)

    # check if user with provided username actually exists
    if not user:
        return make_response("Error: Bad username!", 400)

    hasher = PasswordHasher()

    # check if provided password matches the password in db
    try:
        hasher.verify(user['password'], password)
    except VerifyMismatchError:
        return make_response("Error: password does not match", 400)

    config = Settings()

    token = jwt.encode({
        "username": username,
        "password": password
    }, config.jwt_secret, algorithm="HS256")

    return make_response(token)
from flask import make_response
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flaskr.settings import Settings
import jwt


from flaskr.blueprints.Users.views import findUserByUsername

def authLogInView(request):
    # check if both username and password are provided
    try:
        user_id = request.form['user_id']
        password = request.form['password']
        role = request.form['role']
    except KeyError:
        return make_response("Error: Bad request data!", 400)

    user = findUserByUsername(user_id)

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

    # creating jwt token with specified data as payload
    token = jwt.encode({
        "user_id": user_id,
        "password": password,
        "role": role
    }, config.jwt_secret, algorithm="HS256")


    return make_response(token)
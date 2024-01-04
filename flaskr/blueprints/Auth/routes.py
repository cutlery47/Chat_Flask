from flask import Blueprint, request

# VIEW IMPORTS
from flaskr.blueprints.Auth.views import authLogInView
from flaskr.blueprints.Users.views import addUserView

auth_bp = Blueprint("Auth", __name__)

@auth_bp.route('/register/', methods=['POST'])
def authSignUp():
    """ adds a new user to the system """

    return addUserView(request)


@auth_bp.route('/login/', methods=['POST'])
def authLogIn():
    """ confirms credentials and returns a token """

    return authLogInView(request)
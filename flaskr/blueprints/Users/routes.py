from flask import Blueprint, request

# VIEW IMPORTS
from flaskr.blueprints.Users.views import getUsersView
from flaskr.blueprints.Users.views import getUserByUsernameView
from flaskr.blueprints.Users.views import deleteUserView
from flaskr.blueprints.Users.views import updateUserView

# api for users
users_bp = Blueprint("Users", __name__)

@users_bp.route("/", methods=['GET'])
def getUsers():
    """ returns all the users in the system """
    return getUsersView(request)

@users_bp.route("/<user_id>", methods=['GET'])
def getUserByUsername(user_id):
    """ returns a specific user by provided id"""
    return getUserByUsernameView(request, user_id)

@users_bp.route("/<user_id>", methods=['DELETE'])
def deleteUser(user_id):
    """ deletes a specific user """
    return deleteUserView(request, user_id)

@users_bp.route("/<user_id>", methods=['PUT'])
def updateUser(user_id):
    """ updates data of a specific user"""
    return updateUserView(request, user_id)


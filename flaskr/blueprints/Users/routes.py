from flask import Blueprint, request

# VIEW IMPORTS
from flaskr.blueprints.Users.views import getUsersView
from flaskr.blueprints.Users.views import addUserView
from flaskr.blueprints.Users.views import getUserView
from flaskr.blueprints.Users.views import deleteUserView
from flaskr.blueprints.Users.views import updateUserView

users_bp = Blueprint("Users", __name__)

@users_bp.route("/", methods=['GET'])
def getUsers():
    return getUsersView(request)

@users_bp.route("/", methods=['POST'])
def addUser():
    return addUserView(request)

@users_bp.route("/<int:user_id>", methods=['GET'])
def getUser(user_id):
    return getUserView(request, user_id)

@users_bp.route("/<int:user_id>", methods=['DELETE'])
def deleteUser(user_id):
    return deleteUserView(request, user_id)

@users_bp.route("/<int:user_id>", methods=['PUT'])
def updateUser(user_id):
    return updateUserView(request, user_id)
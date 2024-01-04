from flask import Blueprint, request

walls_bp = Blueprint("Walls", __name__)

@walls_bp.route("/<user_id>", methods=['GET'])
def getWallPosts(user_id):
    """ returns user's wall """
    return ...

@walls_bp.route("/<user_id>/post/", methods=['POST'])
def addWallPost(user_id):
    """ adds a new post on a user's wall """
    return ...

@walls_bp.route("/<user_id>/<int:post_id>", methods=['DELETE'])
def deleteWallPost(user_id, post_id):
    """ deletes a post on the wall """
    return ...

@walls_bp.route("/<user_id>/<int:post_id>", methods=['POST'])
def likeWallPost(user_id, post_id):
    """ adds a 'like' to a user post """
    return ...
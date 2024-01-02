from flask import Blueprint, request

from flaskr.blueprints.Chats.views import getChatsView
from flaskr.blueprints.Chats.views import getChatView
from flaskr.blueprints.Chats.views import sendChatMessageView
from flaskr.blueprints.Chats.views import getChatMessagesView
from flaskr.blueprints.Chats.views import addChatUserView
from flaskr.blueprints.Chats.views import removeChatUserView
from flaskr.blueprints.Chats.views import createChatView

chats_bp = Blueprint("Chats", __name__)

@chats_bp.route("/", methods=['GET'])
def getChats():
    """ returns information about each user's chat"""
    return getChatsView(request)

@chats_bp.route("/create/", methods=['POST'])
def createChat():
    """ creates a new chat """
    return createChatView(request)

@chats_bp.route("/<chat_id>", methods=['GET'])
def getChat(chat_id):
    """ returns information about specific user's chat """
    return getChatView(request, chat_id)

@chats_bp.route("/<chat_id>/messages/", methods=['GET'])
def getChatMessages(chat_id):
    """ returns all the chat messages """
    return getChatMessagesView(request, chat_id)

@chats_bp.route("/<chat_id>/messages/", methods=['POST'])
def sendChatMessage(chat_id):
    """ sends a message to the chat """
    return sendChatMessageView(request, chat_id)

@chats_bp.route("/<chat_id>/add/", methods=['POST'])
def addChatUser(chat_id):
    """ adds a new user to the chat"""
    return addChatUserView(request, chat_id)

@chats_bp.route("/<chat_id>/remove/", methods=['POST'])
def removeChatUser(chat_id):
    """ removes a user from the chat"""
    return removeChatUserView(request, chat_id)




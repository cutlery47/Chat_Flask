from flaskr.settings import connectToDB
from flask import make_response
from pypika import Query, Table
from flaskr.blueprints.Users.views import validateToken
from flaskr.blueprints.Users.views import findUserByUsername
from flaskr.settings import decodeJWT
import datetime

def getChatsView(request):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    user_data = decodeJWT(request.form['token'])
    username = user_data['username']

    db = connectToDB()
    cur = db.cursor()

    # sql query which returns chat_id of each chat that the user participates in
    user_chats = Table('User_Chats')
    chats = Table('Chats')
    q = Query.from_(user_chats).select(
        user_chats.chatname
    ).where(
        user_chats.username == username
    )

    cur.execute(q.get_sql())
    chat_ids = cur.fetchall()

    chat_data = []
    for id in chat_ids:
        q = Query.from_(chats).select(
            chats.chatname,
            chats.created_at,
            chats.about
        ).where(
            chats.chatname == id[0]
        )
        cur.execute(q.get_sql())
        chat_data.append(cur.fetchone())

    response = []
    for data in chat_data:
        response.append(
            {
                'chat_name': data[0],
                'chat_created_at': data[1],
                'chat_about': data[2]
            }
        )

    return make_response(response)

def getChatView(request, chat_id):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    user_data = decodeJWT(request.form['token'])
    username = user_data['username']

    # check if user is a chat participant
    if not validateChatPartition(username, chat_id):
        return make_response("Error: You are not apart of this chat...", 403)

    db = connectToDB()
    cur = db.cursor()

    chats = Table('Chats')
    q = Query.from_(chats).select(
        chats.chatname,
        chats.created_at,
        chats.about
    ).where(
        chats.chatname == chat_id
    )

    cur.execute(q.get_sql())
    data = cur.fetchone()

    response = {
        'chat_name': data[0],
        'chat_created_at': data[1],
        'chat_about': data[2]
    }

    return make_response(response)

def createChatView(request):
    try:
        chatname = request.form['chatname']
        about = request.form['about']
    except KeyError:
        return make_response("Error: Chat data was not provided...", 400)

    if findChatByName(chatname):
        return make_response("Error: Chat with provided name already exists...", 400)

    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    user_data = decodeJWT(request.form['token'])
    username = user_data['username']

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%S:%S")

    db = connectToDB()
    cur = db.cursor()

    chats = Table('Chats')
    q = Query.into(chats).columns(
        'chatname',
        'created_at',
        'about'
    ).insert(
        chatname,
        dt,
        about
    )

    cur.execute(q.get_sql())

    user_chats = Table('User_Chats')
    q = Query.into(user_chats).columns(
        'username',
        'chatname'
    ).insert(
        username,
        chatname
    )

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response('Success: New chat has been created successfully')

def sendChatMessageView(request, chat_id):
    return

def getChatMessagesView(request, chat_id):
    return

def addChatUserView(request, chat_id):
    try:
        guest = request.form['guest']
    except KeyError:
        return make_response("Error: Guest user was not provided...", 400)

    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    user_data = decodeJWT(request.form['token'])
    username = user_data['username']

    if not findUserByUsername(guest):
        return make_response("Error: The guest user that you provided does not exist...", 400)

    if not validateChatPartition(username, chat_id):
        return make_response("Error: You are not apart of this chat or this chat does not exist...", 403)

    if validateChatPartition(guest, chat_id):
        return make_response("Error: The guest user is already in the chat...", 400)

    db = connectToDB()
    cur = db.cursor()

    user_chats = Table('User_Chats')
    q = Query.into(user_chats).columns(
        'chatname',
        'username'
    ).insert(
        chat_id,
        guest
    )

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: A new user has been successfully added to the chat!")

def removeChatUserView(request, chat_id):
    return

def validateChatPartition(username, chat_id):
    db = connectToDB()
    cur = db.cursor()

    user_chats = Table('User_Chats')
    q = Query.from_(user_chats).select(
        user_chats.chatname
    ).where(
        user_chats.username == username
    )

    cur.execute(q.get_sql())
    chats = cur.fetchall()

    for chat in chats:
        if chat[0] == chat_id:
            return True

    return False

def findChatByName(chatname):
    db = connectToDB()
    cur = db.cursor()

    chats = Table('Chats')
    q = Query.from_(chats).select(
        chats.chatname,
        chats.created_at,
        chats.about
    ).where(
        chats.chatname == chatname
    )

    cur.execute(q.get_sql())
    data = cur.fetchone()

    cur.close()
    db.close()

    if data:
        return {
            'chatname': data[0],
            'created_at': data[1],
            'about': data[2]
        }
    else:
        return None


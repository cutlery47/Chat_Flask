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
    user_id = user_data['user_id']

    db = connectToDB()
    cur = db.cursor()

    # sql query which returns chat_id of each chat that the user participates in
    user_chats = Table('User_Chats')
    chats = Table('Chats')
    q = Query.from_(user_chats).select(
        user_chats.chat_id
    ).where(
        user_chats.user_id == user_id
    )

    cur.execute(q.get_sql())
    chat_ids = cur.fetchall()

    chat_data = []
    for id in chat_ids:
        q = Query.from_(chats).select(
            chats.chat_id,
            chats.created_at,
            chats.about
        ).where(
            chats.chat_id == id[0]
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
    user_id = user_data['user_id']

    # check if user is a chat participant
    if not validateChatPartition(user_id, chat_id):
        return make_response("Error: You are not apart of this chat or this chat does not exist...", 403)

    db = connectToDB()
    cur = db.cursor()

    chats = Table('Chats')
    q = Query.from_(chats).select(
        chats.chat_id,
        chats.created_at,
        chats.about
    ).where(
        chats.chat_id == chat_id
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
        chat_id = request.form['chat_id']
        about = request.form['about']
    except KeyError:
        return make_response("Error: Chat data was not provided...", 400)

    if findChatByName(chat_id):
        return make_response("Error: Chat with provided name already exists...", 400)

    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    user_data = decodeJWT(request.form['token'])
    user_id = user_data['user_id']

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%S:%S")

    db = connectToDB()
    cur = db.cursor()

    chats = Table('Chats')
    q = Query.into(chats).columns(
        'chat_id',
        'created_at',
        'about'
    ).insert(
        chat_id,
        dt,
        about
    )

    cur.execute(q.get_sql())

    user_chats = Table('User_Chats')
    q = Query.into(user_chats).columns(
        'user_id',
        'chat_id'
    ).insert(
        user_id,
        chat_id
    )

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response('Success: New chat has been created successfully')

def sendChatMessageView(request, chat_id):
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        text = request.form['text']
    except KeyError:
        return make_response('Error: Bad request data...', 400)

    if not validateToken(request):
        return make_response('Error: Token was not provided or is not valid...', 400)

    user_data = decodeJWT(request.form['token'])
    user_id = user_data['user_id']

    if not validateChatPartition(user_id, chat_id):
        return make_response('Error: You are not apart of this chat or this chat does not exist...', 400)

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%S:%S")

    db = connectToDB()
    cur = db.cursor()

    messages = Table('Messages')
    q = Query.into(messages).columns(
        'chat_id',
        'sender_id',
        'sender_first_name',
        'sender_last_name',
        'sent_at',
        'text'
    ).insert(
        chat_id,
        user_id,
        first_name,
        last_name,
        dt,
        text
    )

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response('Success: The message has been successfully sent!')

def getChatMessagesView(request, chat_id):
    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    user_data = decodeJWT(request.form['token'])
    user_id = user_data['user_id']

    if not validateChatPartition(user_id, chat_id):
        return make_response("Error: You are not apart of this chat or this chat does not exist...", 400)

    db = connectToDB()
    cur = db.cursor()

    messages = Table('Messages')
    q = Query.from_(messages).select(
        messages.sender_id,
        messages.sender_first_name,
        messages.sender_last_name,
        messages.sent_at,
        messages.text
    ).where(
        messages.chat_id == chat_id
    )

    cur.execute(q.get_sql())
    data = cur.fetchall()

    response = []
    for dat in data:
        response.append(
            {
                'sender_id': dat[0],
                'sender_first_name': dat[1],
                'sender_last_name': dat[2],
                'datetime': dat[3],
                'text': dat[4]
            }
        )

    cur.close()
    db.close()

    return make_response(response)

def addChatUserView(request, chat_id):
    try:
        guest = request.form['guest']
    except KeyError:
        return make_response("Error: Guest user was not provided...", 400)

    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    user_data = decodeJWT(request.form['token'])
    user_id = user_data['user_id']

    if not findUserByUsername(guest):
        return make_response("Error: The guest user that you provided does not exist...", 400)

    if not validateChatPartition(user_id, chat_id):
        return make_response("Error: You are not apart of this chat or this chat does not exist...", 403)

    if validateChatPartition(guest, chat_id):
        return make_response("Error: The guest user is already in the chat...", 400)

    db = connectToDB()
    cur = db.cursor()

    user_chats = Table('User_Chats')
    q = Query.into(user_chats).columns(
        'chat_id',
        'user_id'
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
    try:
        guest = request.form['guest']
    except KeyError:
        return make_response('Error: Guest user was not provided...', 400)

    if not validateToken(request):
        return make_response('Error: Token was not provided or is not valid...', 400)

    user_data = decodeJWT(request.form['token'])
    user_id = user_data['user_id']

    if not findUserByUsername(guest):
        return make_response("Error: The guest user that you provided does not exist...", 400)

    if not validateChatPartition(user_id, chat_id):
        return make_response("Error: You are not apart of this chat or this chat does not exist...", 403)

    if not validateChatPartition(guest, chat_id):
        return make_response("Error: The guest user is not apart of this chat...", 400)

    db = connectToDB()
    cur = db.cursor()

    user_chats = Table('User_Chats')
    q = Query.from_(user_chats).delete().where(user_chats.user_id == guest)

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    return make_response('Success: User was successfully deleted from the chat!')

def validateChatPartition(user_id, chat_id):
    db = connectToDB()
    cur = db.cursor()

    user_chats = Table('User_Chats')
    q = Query.from_(user_chats).select(
        user_chats.chat_id
    ).where(
        user_chats.user_id == user_id
    )

    cur.execute(q.get_sql())
    chats = cur.fetchall()

    for chat in chats:
        if chat[0] == chat_id:
            return True

    return False

def findChatByName(chat_id):
    db = connectToDB()
    cur = db.cursor()

    chats = Table('Chats')
    q = Query.from_(chats).select(
        chats.chat_id,
        chats.created_at,
        chats.about
    ).where(
        chats.chat_id == chat_id
    )

    cur.execute(q.get_sql())
    data = cur.fetchone()

    cur.close()
    db.close()

    if data:
        return {
            'chat_id': data[0],
            'created_at': data[1],
            'about': data[2]
        }
    else:
        return None


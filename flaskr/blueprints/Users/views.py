from flaskr.settings import connectToDB
from flask import make_response
from pypika import Query, Table
from argon2 import PasswordHasher
from flaskr.settings import Settings
import jwt


def getUsersView(request):
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    db = connectToDB()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).select(
        users.id,
        users.username,
        users.first_name,
        users.last_name,
        users.role
    )

    cur.execute(q.get_sql())
    data = cur.fetchall()

    response = []
    for el in data:
        dat = {
            'id': el[0],
            'username': el[1],
            'first_name': el[2],
            'last_name': el[3],
            'role': el[4]
        }
        response.append(dat)

    cur.close()
    db.close()

    #200
    return make_response(response)

def addUserView(request):
    try:
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
    except KeyError as error:
        return make_response("Error: Bad user data...", 400)

    if findUserByUsername(username):
        return make_response("Error: User with the username already exists...", 400)

    db = connectToDB()
    cur = db.cursor()

    hasher = PasswordHasher()
    hashed_password = hasher.hash(password)

    users = Table('Users')
    q = Query.into(users).columns(
        'username',
        'password',
        'first_name',
        'last_name',
        'role'
    ).insert(
        username,
        hashed_password,
        first_name,
        last_name,
        role
    )

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: User created successfully!")

def getUserByIdView(request, user_id):
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    data = findUserById(user_id)
    if not data:
        return make_response("Error: User was not found by specified id", 404)

    # hiding password from random users
    data.pop('password')

    # 200
    return make_response(data)

# deprecated I guess
def getUserByUsernameView(request, username):
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    data = findUserByUsername(username)
    if not data:
        return make_response("Error: User was not found by specified username", 404)

    # hiding password from random users
    data.pop('password')

    # 200
    return make_response(data)

def deleteUserView(request, user_id):
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    if not validatePermission(request, user_id):
        return make_response("Error: You are not allowed to perform desired request...", 403)

    if not findUserById(user_id):
        return make_response("Error: User was not found by specified id", 404)

    db = connectToDB()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).delete().where(users.id == user_id)

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: Specified user has been deleted")

def updateUserView(request, user_id):
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    if not validatePermission(request, user_id):
        return make_response("Error: You are not allowed to perform desired request...", 403)

    if not findUserById(user_id):
        return make_response("Error: User was not found by specified id", 404)

    db = connectToDB()
    cur = db.cursor()

    users = Table('Users')
    # update query object but the data fields to be updated are not provided
    update_query = Query.update(users).where(users.id == user_id)
    # providing the data fields
    for field in request.form:
        # if a new password is provided - hash and update the password
        if field == 'password':
            hasher = PasswordHasher()
            hashed_password = hasher.hash(request.form[field])
            update_query = update_query.set(field, hashed_password)
        # token field simply doesnt exist
        elif field == "token":
            continue
        else:
            update_query = update_query.set(field, request.form[field])

    cur.execute(update_query.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: User updated successfully")

def findUserById(user_id):
    """ checks if user with provided id is present in the system """

    db = connectToDB()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).select(
        users.id,
        users.username,
        users.password,
        users.first_name,
        users.last_name,
        users.role
    ).where(
        users.id == user_id
    )

    cur.execute(q.get_sql())
    data = cur.fetchone()

    cur.close()
    db.close()

    # if returned data package is not empty - the data has been found
    if data:
        return {
            'id': data[0],
            'username': data[1],
            'password': data[2],
            'first_name': data[3],
            'last_name': data[4],
            'role': data[5]
        }
    else:
        return None

def findUserByUsername(username):
    """ checks if user with provided username is present in the system """

    db = connectToDB()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).select(
        users.id,
        users.username,
        users.password,
        users.first_name,
        users.last_name,
        users.role
    ).where(
        users.username == username
    )

    cur.execute(q.get_sql())
    data = cur.fetchone()

    cur.close()
    db.close()

    # if returned data package is not empty - the data has been found
    if data:
        return {
            'id': data[0],
            'username': data[1],
            'password': data[2],
            'first_name': data[3],
            'last_name': data[4],
            'role': data[5]
        }
    else:
        return None

def validateToken(request):
    config = Settings()
    hasher = PasswordHasher()

    try:
        token = request.form['token']
    except KeyError:
        return False

    data = jwt.decode(token, config.jwt_secret, algorithms="HS256")

    username = data['username']
    password = data['password']

    user = findUserByUsername(username)
    if not user:
        return False

    if hasher.verify(user['password'], password):
        return True
    else:
        return False

def validatePermission(request, user_id):
    config = Settings()

    try:
        token = request.form['token']
    except KeyError:
        return False

    data = jwt.decode(token, config.jwt_secret, algorithms="HS256")

    username = data['username']
    role = data['role']

    if role == 'admin':
        return True

    if findUserById(user_id) == findUserByUsername(username):
        return True
    else:
        return False

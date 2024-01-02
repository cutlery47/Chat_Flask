from flaskr.settings import connectToDB
from flask import make_response
from pypika import Query, Table
from argon2 import PasswordHasher
from flaskr.settings import Settings
from flaskr.settings import decodeJWT
import jwt


def getUsersView(request):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    db = connectToDB()
    cur = db.cursor()

    # sql query
    users = Table('Users')
    q = Query.from_(users).select(
        users.username,
        users.first_name,
        users.last_name,
        users.role
    )

    cur.execute(q.get_sql())
    data = cur.fetchall()

    # collect all the data into a list of dicts
    response = []
    for el in data:
        dat = {
            'username': el[0],
            'first_name': el[1],
            'last_name': el[2],
            'role': el[3]
        }
        response.append(dat)

    cur.close()
    db.close()

    #200
    return make_response(response)

def addUserView(request):
    # check if all the data for user creation is present
    try:
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
    except KeyError as error:
        return make_response("Error: Bad user data...", 400)

    # check if username is unique
    if findUserByUsername(username):
        return make_response("Error: User with the username already exists...", 400)

    db = connectToDB()
    cur = db.cursor()

    # hashing incoming password
    hasher = PasswordHasher()
    hashed_password = hasher.hash(password)

    # sql query
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

# deprecated I guess
def getUserByUsernameView(request, username):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    # check if requested user exists
    data = findUserByUsername(username)
    if not data:
        return make_response("Error: User was not found by specified username", 404)

    # hiding password from random users
    data.pop('password')

    # 200
    return make_response(data)

def deleteUserView(request, username):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    # check if user is allowed to perform deletion
    if not validatePermission(request, username):
        return make_response("Error: You are not allowed to perform desired request...", 403)

    # check if requested user exists
    if not findUserByUsername(username):
        return make_response("Error: User was not found by specified username", 404)

    db = connectToDB()
    cur = db.cursor()

    # sql query
    users = Table('Users')
    q = Query.from_(users).delete().where(users.username == username)

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: Specified user has been deleted")

def updateUserView(request, username):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    # check if user is allowed to perform edit
    if not validatePermission(request, username):
        return make_response("Error: You are not allowed to perform desired request...", 403)

    # check if requested user exists
    if not findUserByUsername(username):
        return make_response("Error: User was not found by specified username", 404)

    db = connectToDB()
    cur = db.cursor()

    # sql query
    users = Table('Users')
    # update query object but the data fields to be updated are not provided
    update_query = Query.update(users).where(users.id == username)
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

def findUserByUsername(username):
    """ checks if user with provided username is present in the system """
    db = connectToDB()
    cur = db.cursor()

    # sql query
    users = Table('Users')
    q = Query.from_(users).select(
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
            'username': data[0],
            'password': data[1],
            'first_name': data[2],
            'last_name': data[3],
            'role': data[4]
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

def validatePermission(request, username):
    config = Settings()

    try:
        token = request.form['token']
    except KeyError:
        return False

    data = decodeJWT(token)

    jwt_username = data['username']
    jwt_role = data['role']

    if jwt_role == 'admin':
        return True

    if findUserByUsername(jwt_username) == findUserByUsername(username):
        return True
    else:
        return False

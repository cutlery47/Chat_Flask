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
        users.user_id,
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
            'user_id': el[0],
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
        user_id = request.form['user_id']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
    except KeyError as error:
        return make_response("Error: Bad user data...", 400)

    # check if user_id is unique
    if findUserByUsername(user_id):
        return make_response("Error: User with the user_id already exists...", 400)

    db = connectToDB()
    cur = db.cursor()

    # hashing incoming password
    hasher = PasswordHasher()
    hashed_password = hasher.hash(password)

    # sql query
    users = Table('Users')
    q = Query.into(users).columns(
        'user_id',
        'password',
        'first_name',
        'last_name',
        'role'
    ).insert(
        user_id,
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
def getUserByUsernameView(request, user_id):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    # check if requested user exists
    data = findUserByUsername(user_id)
    if not data:
        return make_response("Error: User was not found by specified user_id", 404)

    # hiding password from random users
    data.pop('password')

    # 200
    return make_response(data)

def deleteUserView(request, user_id):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token was not provided or is not valid...", 400)

    # check if user is allowed to perform deletion
    if not validatePermission(request, user_id):
        return make_response("Error: You are not allowed to perform desired request...", 403)

    # check if requested user exists
    if not findUserByUsername(user_id):
        return make_response("Error: User was not found by specified user_id", 404)

    db = connectToDB()
    cur = db.cursor()

    # sql query
    users = Table('Users')
    q = Query.from_(users).delete().where(users.user_id == user_id)

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: Specified user has been deleted")

def updateUserView(request, user_id):
    # check if jwt token is valid
    if not validateToken(request):
        return make_response("Error: Token is not provided or is not valid...", 400)

    # check if user is allowed to perform edit
    if not validatePermission(request, user_id):
        return make_response("Error: You are not allowed to perform desired request...", 403)

    # check if requested user exists
    if not findUserByUsername(user_id):
        return make_response("Error: User was not found by specified user_id", 404)

    db = connectToDB()
    cur = db.cursor()

    # sql query
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

def findUserByUsername(user_id):
    """ checks if user with provided user_id is present in the system """
    db = connectToDB()
    cur = db.cursor()

    # sql query
    users = Table('Users')
    q = Query.from_(users).select(
        users.user_id,
        users.password,
        users.first_name,
        users.last_name,
        users.role
    ).where(
        users.user_id == user_id
    )

    cur.execute(q.get_sql())
    data = cur.fetchone()

    cur.close()
    db.close()

    # if returned data package is not empty - the data has been found
    if data:
        return {
            'user_id': data[0],
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
    print(data)

    user_id = data['user_id']
    password = data['password']

    user = findUserByUsername(user_id)
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

    data = decodeJWT(token)

    jwt_user_id = data['user_id']
    jwt_role = data['role']

    if jwt_role == 'admin':
        return True

    if findUserByUsername(jwt_user_id) == findUserByUsername(user_id):
        return True
    else:
        return False

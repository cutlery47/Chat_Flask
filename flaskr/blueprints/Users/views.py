from flaskr.settings import connectToDB
from flask import make_response
from pypika import Query, Table
from argon2 import PasswordHasher

def getUsersView(request):
    db = connectToDB()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).select(
        users.id,
        users.username,
        users.first_name,
        users.last_name
    )

    cur.execute(q.get_sql())
    data = cur.fetchall()

    response = []
    for el in data:
        dat = {
            'id': el[0],
            'username': el[1],
            'first_name': el[2],
            'last_name': el[3]
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
    except KeyError as error:
        return make_response("Error: Bad user data", 400)

    db = connectToDB()
    cur = db.cursor()

    hasher = PasswordHasher()
    hashed_password = hasher.hash(password)

    users = Table('Users')
    q = Query.into(users).columns(
        'username',
        'password',
        'first_name',
        'last_name'
    ).insert(
        username,
        hashed_password,
        first_name,
        last_name
    )

    cur.execute(q.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: User added successfully!")

def getUserView(request, user_id):
    if not foundUserById(user_id):
        return make_response("Error: User was not found by specified id", 404)

    db = connectToDB()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).select(
        users.id,
        users.username,
        users.first_name,
        users.last_name
    ).where(
        users.id == user_id
    )

    cur.execute(q.get_sql())
    data = cur.fetchall()

    response = []
    for el in data:
        dat = {
            'id': el[0],
            'username': el[1],
            'first_name': el[2],
            'last_name': el[3]
        }
        response.append(dat)

    cur.close()
    db.close()

    #200
    return make_response(response)

def deleteUserView(request, user_id):
    if not foundUserById(user_id):
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
    if not foundUserById(user_id):
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
        else:
            update_query = update_query.set(field, request.form[field])

    cur.execute(update_query.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: User updated successfully")


def foundUserById(user_id):
    """ checks if user with provided id is present in the system """
    db = connectToDB()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).select(
        users.id
    ).where(
        users.id == user_id
    )

    cur.execute(q.get_sql())
    data = cur.fetchall()

    cur.close()
    db.close()

    if len(data) != 0:
        return True
    else:
        return False
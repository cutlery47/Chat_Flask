from flaskr.settings import connect_to_db
from flask import make_response
from pypika import Query, Table

def getUsersView(request):
    db = connect_to_db()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).select(
        users.id,
        users.username,
        users.password,
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
            'password': el[2],
            'first_name': el[3],
            'last_name': el[4]
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
        return make_response("Error: Bad request data", 400)

    db = connect_to_db()
    cur = db.cursor()

    users = Table('Users')
    q = Query.into(users).columns(
        'username',
        'password',
        'first_name',
        'last_name'
    ).insert(
        username,
        password,
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

    db = connect_to_db()
    cur = db.cursor()

    users = Table('Users')
    q = Query.from_(users).select(
        users.id,
        users.username,
        users.password,
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
            'password': el[2],
            'first_name': el[3],
            'last_name': el[4]
        }
        response.append(dat)

    cur.close()
    db.close()

    #200
    return make_response(response)

def deleteUserView(request, user_id):
    if not foundUserById(user_id):
        return make_response("Error: User was not found by specified id", 404)

    db = connect_to_db()
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

    db = connect_to_db()
    cur = db.cursor()

    users = Table('Users')
    update_query = Query.update(users).where(users.id == user_id)
    for field in request.form:
        update_query = update_query.set(field, request.form[field])

    cur.execute(update_query.get_sql())
    db.commit()

    cur.close()
    db.close()

    #200
    return make_response("Success: User updated successfully")



def foundUserById(user_id):
    db = connect_to_db()
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
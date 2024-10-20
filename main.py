from typing import Tuple
from flask import Flask, jsonify, request, render_template, make_response, session, abort
from flask_mysqldb import MySQL

app = Flask(__name__)

USERID = 'userID'
app.secret_key='Mid_Project'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Password1'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'mid_project'
mysql = MySQL(app)

# MYSQL functionality (defined here because these are dependent on the mysql variable at runtime)
def MySQL_Select(query : str) -> Tuple[Tuple[str]]:
    # Basically if everyone works just return the select results
    # Otherwise abort with a descriptive message
    cur = mysql.connection.cursor()
    public_results : Tuple[Tuple[str]] = None
    try:
        cur.execute(query)
        public_results = cur.fetchall()
    except Exception as e:
        abort(500, str(e))
    finally:
        cur.close()
    return public_results

def MySQL_Insert(query : str) -> None:
    # Basically if everyone works just insert
    # Otherwise abort with a descriptive message
    cur = mysql.connection.cursor()
    try:
        cur.execute(query)
        mysql.connection.commit()
    except Exception as e:
        abort(500, str(e))
    finally:
        cur.close()
    
# Main functionality

@app.route('/')
def home():
    # public endpoint that displays all public books

    # Get all of the public books in order to display them
    public_results = MySQL_Select('SELECT * FROM mid_project.book WHERE MembersOnly=false')

    book_results = []

    for result in public_results:
        book_info = {}
        book_info["ID"] = result[0]
        book_info["Title"] = result[1]
        book_info["Author"] = result[2]
        # last result, result[3] is whether it should be publically displayed or not, we don't need to display it
        book_results.append(book_info)

    return render_template('home.html', books = book_results, number_of_books = len(public_results))

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.cookies.get(USERID)
    if username:
        # If cookie exists, then we auto redirec to profile
        return app.redirect('/profile')
    else:
        THIRTY_MINUTES_IN_SECONDS = 1800
        if request.method == 'POST':
            # then we handle cookie generation; if form is non empty, then we create cookie with that username
            username_from_form = request.form.get('username')
            if username_from_form:
                resp = app.redirect('/profile')
                resp.set_cookie(USERID, username_from_form, max_age=THIRTY_MINUTES_IN_SECONDS)
                session[username_from_form] = session.get(username_from_form, 0) # default value is 0, it will be autoincremented if have valid cookies on profile view
            else:
                resp = make_response('Cookie is not created; username is empty')
            return resp
        else:
            return render_template('login_form.html')
        
@app.route('/profile')
def profile():
    username = request.cookies.get(USERID)
    if not username:
        return app.redirect('/login')
    session[username] = session.get(username, 0) + 1

    # Get all of the private books in order to display them
    all_results = MySQL_Select('SELECT * FROM mid_project.book')

    book_results = []

    for result in all_results:
        book_info = {}
        book_info["ID"] = result[0]
        book_info["Title"] = result[1]
        book_info["Author"] = result[2]
        # last result, result[3] is whether it should be publically displayed or not, we don't need to display it
        book_results.append(book_info)

    return render_template('profile.html', data={"user":username,"time":session[username],"books":book_results,"number_of_books":len(all_results)})

@app.route('/logout')
def logout():
    username = request.cookies.get(USERID)
    return_to_login = app.redirect('/login')
    if not username:
        return return_to_login
    return_to_login.delete_cookie(USERID)
    session.pop(username)
    return return_to_login

@app.route('/test_select')
def test_select():
    # use for debugging
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM book')
    results = cur.fetchall()
    print(results)
    cur.close()
    return jsonify(results), 200

# CRUD
# TODO: enforce JWT authentication, don't let random people update database
# maybe add error handling (try except...) and throw internal server error if database operation fails
@app.route('/book', methods=['POST', 'GET'])
def books():
    # handle book database CRUD operations
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        # Create a book from form data
        ID = request.form.get("ID")
        Title = request.form.get("Title")
        Author = request.form.get("Author")
        MembersOnly = request.form.get("MembersOnly")

        # If any of these are missing, raise bad request
        if not all((ID,Title,Author,MembersOnly)):
            abort(400)

        MembersOnly = bool(MembersOnly)

        MySQL_Insert("INSERT INTO mid_project.book Values({0},'{1}','{2}',{3})".format(ID, Title, Author, MembersOnly))

        return 'Done!', 200
    elif request.method == 'GET':
        # Get all of the books
        cur.execute('SELECT * FROM book')
        results = cur.fetchall()
        cur.close()
        return jsonify(results), 200
    
    cur.close() # Invalid method type, close cursor before aborting
    abort(400)

@app.route('/book/<id>', methods=['GET', 'PUT', 'DELETE'])
def book(id):
    # handle book database CRUD operations
    cur = mysql.connection.cursor()
    if request.method == 'GET':
        pass
    elif request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        pass

# Error handlers
@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify(error=str(e)), 400

@app.errorhandler(401)
def handle_unauthorized(e):
    return jsonify(error=str(e)), 401

@app.errorhandler(404)
def handle_page_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def handle_internal_server_error(e):
    return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)
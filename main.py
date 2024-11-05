from typing import Tuple
from flask import Flask, jsonify, request, render_template, make_response, session, abort
from flask_mysqldb import MySQL
from functools import wraps
from werkzeug.utils import secure_filename
import os
import jwt

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.txt']
app.config['UPLOAD_PATH'] = 'uploads/'

USERID = 'userID'
app.config['SECRET_KEY']='Mid_Project'

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

def MySQL_RunQuery(query : str) -> None:
    # Basically if everyone works just perform the query
    # Otherwise abort with a descriptive message
    cur = mysql.connection.cursor()
    try:
        cur.execute(query)
        mysql.connection.commit()
    except Exception as e:
        abort(500, str(e))
    finally:
        cur.close()

# Token verification for JWT Auth Login
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # You have the JWT token; but you cannot access a page or something?
        # Simply add: ?Authorization={TOKEN} in the URL
        # Or add a bearer auth token
        AUTHORIZATION = 'Authorization'
        token = request.headers.get(AUTHORIZATION) or request.args.get(AUTHORIZATION)
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        # Pass the current user to the route
        return f(current_user, *args, **kwargs)
    return decorated

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
    # The creation and management of users is outside of this project's scope
    # I'm making the decision to hardcode the credentials so we simply validate the credentials
    # are as follows: Username: admin; Password: password
    # as always this can be expanded upon; but this is "good enough" for now
    HARDCODED_USER = "admin"
    HARDCODED_PASSWORD = "password"

    if request.method == 'POST':
        username_from_form = request.form.get('username')
        password_from_form = request.form.get('password')
        if username_from_form == HARDCODED_USER and password_from_form == HARDCODED_PASSWORD:
            # Generate token
            token = jwt.encode({'username': username_from_form}, app.config['SECRET_KEY'])

            # Generate the session cookie for number of visits (unrelated to jwt token)
            session[username_from_form] = session.get(username_from_form, 0) # default value is 0, it will be autoincremented if have valid cookies on profile view
            return jsonify({'token': token})
        else:
            return jsonify({'message': 'Invalid credentials! This is not the hardcoded user'}), 401
    return render_template('login_form.html')

@app.route('/profile')
@token_required # Authorization is required to enter this page
def profile(current_user):

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

    session[current_user] = session.get(current_user,0) + 1 # keep track of the number of times visited the profile
    return render_template('profile.html', data={"user":current_user,"time": session[current_user],"books":book_results,"number_of_books":len(all_results)})

@app.route('/logout')
@token_required # Authorization is required to enter this page
def logout(current_user):
    return_to_login = app.redirect('/login')
    if not current_user:
        return return_to_login
    session.pop(current_user)
    return return_to_login

@app.route('/test_select')
def test_select():
    # use for debugging
    results = MySQL_Select('SELECT * FROM book')
    print(results)
    return jsonify(results), 200

# CRUD
@app.route('/publicbooks', methods=['GET'])
def public_books():
    if request.method == 'GET':
        # Get all of the public books
        results = MySQL_Select('SELECT * FROM book WHERE MembersOnly=false')
        return jsonify(results), 200
    abort(400)

@app.route('/books', methods=['POST', 'GET'])
@token_required # Authorization is required to enter this page
def books(current_user):
    # handle book database CRUD operations
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

        MySQL_RunQuery("INSERT INTO mid_project.book Values({0},'{1}','{2}',{3})".format(ID, Title, Author, MembersOnly))

        return "Successfully inserted new book with data: ID {0}, Title '{1}', Author '{2}', MembersOnly{3}".format(ID, Title, Author, MembersOnly), 200
    elif request.method == 'GET':
        # Get all books
        results = MySQL_Select('SELECT * FROM book')
        return jsonify(results), 200
    abort(400)

@app.route('/book/<id>', methods=['GET', 'PUT', 'DELETE'])
@token_required # Authorization is required to enter this page
def book(current_user, id):
    # handle book database CRUD operations
    if request.method == 'GET':
        result = MySQL_Select('SELECT * FROM book WHERE ID = {0}'.format(id))
        return jsonify(result), 200
    elif request.method == 'PUT':
        # First we get the existing data
        result = MySQL_Select('SELECT * FROM book WHERE ID = {0}'.format(id))

        # unpack and store into variables
        originalTitle = result[0][1]
        originalAuthor = result[0][2]
        originalMembersOnly = result[0][3]

        # Then we check to see if there is appropriate form data
        Title = request.form.get("Title")
        Author = request.form.get("Author")
        MembersOnly = request.form.get("MembersOnly")

        # Edge case, if there is no form data; then just throw bad request, there needs to be a reason to change this data
        if not any((Title,Author,MembersOnly)):
            abort(400)

        # Take from original data if there is no form data
        Title = Title or originalTitle
        Author = Author or originalAuthor
        MembersOnly = bool(MembersOnly if not MembersOnly is None else originalMembersOnly)

        # Finally do update
        MySQL_RunQuery("UPDATE book SET Title='{0}',Author='{1}',MembersOnly={2} WHERE ID={3}".format(Title,Author,MembersOnly,id))

        return "Successfully updated book with data: ID: {0}, Title '{1}', Author '{2}', MembersOnly {3}".format(id, Title, Author, MembersOnly), 200
    elif request.method == 'DELETE':
        pass

@app.route('/upload')#, methods=['POST'])
@token_required # Authorization is required to enter this page
def upload_file(current_user):
    # handle file upload stuff here
    token = request.headers.get('Authorization')

    return render_template('upload.html')


@app.route('/sendFile',methods=['POST'])

def sendFile():
    uploaded_file = request.files['file']
 
    if uploaded_file.filename != '':
        filename = secure_filename(uploaded_file.filename)
    if os.path.splitext(filename)[1] in app.config['UPLOAD_EXTENSIONS']:
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'],filename))
        return 'uploaded'
    abort(400)


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
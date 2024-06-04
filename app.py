from functools import wraps
import sqlite3
from flask import Flask, redirect, render_template, render_template_string, request, session
from check_url import check_from_url
from key_manager import delete_table, create_key_table, txt_to_db, get_table_info
from werkzeug.security import check_password_hash, generate_password_hash
import re

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if not re.search(r'^.*cdn3.digialm.com/.*\.html$',request.form.get('url')):
            return render_template('error.html', error='Response sheets not found')
        session['url'] = request.form.get('url')
        return redirect('/result')
    return render_template('index.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    result = check_from_url(session.get('url'))
    if not result:
        return render_template('error.html', error='Result can\'t be calculated')
    if request.method == 'POST':
        return render_template_string(result[3])
    return render_template('result.html', correct=result[0], incorrect=result[1], unanswered=result[2])

@app.route('/key_manager', methods=['POST', 'GET'])
@login_required
def key_manager():
    if request.method == 'POST':
        name, key = request.form.get('name'), request.form.get('key')
        if not name or not key:
            return render_template('error.html', error='Values not entered')
        delete_table(name)
        create_key_table(name)
        txt_to_db(key, name)
        return redirect('/key_manager')
    return render_template('key_manager.html', tables = get_table_info())

@app.route('/delete/<key_name>')
@login_required
def delete_key(key_name):
    delete_table(key_name)
    return redirect('/key_manager')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=str(e)), 404

# Error handler for 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error=str(e)), 500

# Error handler for 403
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error=str(e)), 403

# Error handler for 401
@app.errorhandler(401)
def unauthorized(e):
    return render_template('error.html', error=str(e)), 401

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure mod id was submitted
        if not request.form.get("mod_id"):
            return render_template('error.html', error="Must provide moderator id"), 403
        # mod id should contain only alphanumeric
        elif not re.search(r'^\w+$', request.form.get('mod_id')):
            return render_template('error.html', error="Invalid Moderator ID"), 403
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('error.html', error="Must provide password"), 403

        # Query database for mod id
        #try:
        parameter = (request.form.get("mod_id"),)  # Ensure parameter is a tuple
        query = "SELECT * FROM mods WHERE mod_id = ?"

        try:
            with sqlite3.connect('checker.db') as con:
                cur = con.cursor()
                cur.execute(query, parameter)
                rows = cur.fetchall()
        except sqlite3.OperationalError:
            return render_template('error.html', error='Cannot login.')

        # Ensure id exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][1], request.form.get("password")
        ):
            return render_template('error.html', error="invalid username and/or password"), 403

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/key_manager")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        mod_id = request.form.get("mod_id")
        password = request.form.get("password")
        confirmation = request.form.get("confirm")
        if not mod_id:
            return render_template('error.html', error="must provide moderator id"), 400
        elif not re.search(r'^\w+$', mod_id):
            return render_template('error.html', error="Invalid Moderator ID"), 403
        elif not password or not confirmation:
            return render_template('error.html', error="must provide password"), 400
        elif password != confirmation:
            return render_template('error.html', error="password doesn't match with confirmation password"), 400

        try:
            with sqlite3.connect('checker.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO mods (mod_id, password) VALUES (?, ?)",
                        (mod_id, generate_password_hash(password)))
        except ValueError:
            return render_template('error.html', error="user already exists")
        return redirect("/key_manager")
    else:
        return render_template("register.html")




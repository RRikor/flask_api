# http://flask.pocoo.org/docs/1.0/tutorial/views/
import functools

from flask import (Blueprint, flash, g, redirect, render_template, request
                    , session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# Creates blueprint called auth. Rather then registering views directly, views are 
# registered with a blueprint. Then the blueprint is registered with the application in
# a factory function.
# It needs to know where it is defined, so 
# __name__ is passed as 2nd argumet. The url_prefix is where it can be found.
bp = Blueprint('auth', __name__, url_prefix='/auth')

# View 1: register
#  Associates the URL /register with the register view function. When Flask receives
# a request to auth/register it will call the register view 
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is requred.'
        elif not password:
            error = 'Password is required.'
        # Check if username is already registered
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        # If there are no errors, insert the username and password into the DB
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?,?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            # After registering they are redirected to the login page
            return redirect(url_for('auth.login'))
        
        # flash() stores messages that can be retrieved when rendering the template
        flash(error)


# View 2: login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # User is queried and stored in variable
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        # Checks the password against the hashed version
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across requests. The user_id
            # is stored in a new session. The data is stored in a cookie returned
            # to the browser and the browser sends this back with subsequent requests.
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    """
    Runs before the view function, no matter what URL is requested. It checks if 
    a user_id is stored in the session and gets the user data from the DB to store in 
    g.user for the length of the request.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    """
    Removes the user_id from the session so load_logged_in_user() will not load the 
    user on subsequent requests.
    """
    session.clear()
    return redirect(url_for('index'))

def login_requred(view):
    """
    Decorator to check if the user is logged in, so he can create, edit and delete
    blog posts.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return warpped_view
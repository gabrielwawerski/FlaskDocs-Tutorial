import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')


def not_when_logged_in(view):
    """Should redirect to index when blueprint is tagged with this"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None:
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/login', methods=('GET', 'POST'))
@not_when_logged_in
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username or password.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect username or password.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')


@bp.route('/register', methods=('GET', 'POST'))
@not_when_logged_in
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        surname = request.form['surname']
        age = request.form['age']
        db = get_db()
        error = None

        if not username:
            error = 'Username required.'
        elif not password:
            error = 'Password required.'
        elif not name:
            error = 'Name required.'
        elif not surname:
            error = 'Surname required.'
        elif not age:
            error = 'Age required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f'User {username} is already registered.'

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, name, surname, age) VALUES (?, ?, ?, ?, ?)',
                (username, generate_password_hash(password), name, surname, age)
            )
            db.commit()
            del username, password
            return redirect(url_for('auth.login'))
        flash(error)

    return render_template('auth/register.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def logged_in_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

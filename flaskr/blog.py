from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from flaskr.auth import logged_in_required
from flaskr.db import get_db
from . import util

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, post, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@logged_in_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        post = request.form['post']
        error = None

        if not title:
            error = 'Title required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, post, author_id, created)'
                ' VALUES (?, ?, ?, ?)',
                (title, post, g.user['id'], util.timestamp())
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')


@bp.route('/post/<int:id>/update', methods=('GET', 'POST'))
@logged_in_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        post = request.form['post']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, post = ?'
                ' WHERE id = ?',
                (title, post, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)


@bp.route('/post/<int:id>/delete', methods=('POST',))
@logged_in_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/profile/<int:id>/', )
def display_profile(id):
    user = get_db().execute(
        f"SELECT * FROM user WHERE id = {id}"
    ).fetchone()
    return render_template('blog/profile.html', user=user)


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, post, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


def get_post_comments(post_id):
    comments = get_db().execute(
        'SELECT * FROM comment'
        ' WHERE post_id = ?',
        (post_id,)
    ).fetchall()

    if comments is None:
        return None

    return comments


@bp.route('/post/<int:id>/', methods=('POST', 'GET'))
def display_post(id):
    if request.method == 'POST':
        comment = request.form['comment']
        error = None

        if comment is None:
            error = "You have to write something."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment (author_id, post_id, comment, created)'
                ' VALUES (?, ?, ?, ?)',
                (g.user['id'], id, comment, util.timestamp())
            )
            db.commit()
            return redirect(url_for('blog.display_post'))

    post = get_post(id)
    comments = get_post_comments(id)
    return render_template('blog/post.html', post=post, comments=comments)

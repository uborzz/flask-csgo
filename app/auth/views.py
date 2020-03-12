from flask import render_template, session, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash

from .forms import LoginForm
from ..models import User
from ..db import db
from app.auth.flask_user import FlaskUser

from . import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    context = {
        'login_form': login_form
    }

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data

        loaded_user = db.get_user(username)

        if loaded_user and check_password_hash(loaded_user.password, password):
            user = User(username, password)
            login_user(FlaskUser(user))
            flash('Loged in!')
            return redirect(url_for('auth.admin'))
        
        else:
            flash('Wrong login.')
            return redirect(url_for('auth.login'))

    return render_template('login.html', **context)


@auth.route('/admin', methods=['GET'])
def admin():
    context = {}

    return render_template('admin.html', **context)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bye!')
    return redirect(url_for('auth.login'))

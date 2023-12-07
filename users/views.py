# IMPORTS
import logging
from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from flask_login import login_user, current_user, logout_user, login_required
from markupsafe import Markup

from app import db, anonymous_required
from models import User
from users.forms import RegisterForm, LoginForm, ChangePasswordForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    # create signup form object
    form = RegisterForm()

    validation_message = ""
    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('users/register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        date_of_birth=form.date_of_birth.data,
                        postcode=form.postcode.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # log registration
        logging.warning('SECURITY - User registered [%s, %s]', form.email.data, request.remote_addr)

        # add user to session
        session['username'] = form.email.data

        # sends user to setup 2fa page
        return redirect(url_for('users.setup_2fa'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form, validation_message=validation_message)


# view 2fa setup
@users_blueprint.route('/setup_2fa', methods=['GET', 'POST'])
@anonymous_required
def setup_2fa():
    if 'username' not in session:
        return redirect(url_for('index'))

    user = User.query.filter_by(email=session['username']).first()

    if not user:
        return redirect(url_for('index'))

    del session['username']

    return render_template('users/setup_2fa.html', user=user.email, uri=user.get_2fa_uri()), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache', 'Expires': '0'}


# handle failed login attempts
@anonymous_required
def failed_login(form, request, validation_message):
    session['authentication_attempts'] += 1
    logging.warning(f'SECURITY - User login failed. Attempted username: {form.email.data} [{request.remote_addr}]')

    attempts_remaining = 3 - session['authentication_attempts']
    flash(f'You have {attempts_remaining} attempts remaining', 'info')

    return render_template('users/login.html', form=form, validation_message=validation_message)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()
    validation_message = ""

    # store authentication attempts in flask session
    if not session.get('authentication_attempts'):
        session['authentication_attempts'] = 0

    if session['authentication_attempts'] == 2:  # 3 attempts
        flash(Markup('Too many authentication attempts. Please click <a href="/reset">here</a> to reset'), 'danger')
        return render_template('users/login.html')

    if form.validate_on_submit():
        username = User.query.filter_by(email=form.email.data).first()
        password = form.password.data
        postcode = form.postcode.data
        pin = form.pin.data

        if not username or not User.verify_password(username, password):
            return failed_login(form, request, 'Username or password is incorrect')

        if not username.verify_pin(pin) or not username.verify_postcode(postcode):
            return failed_login(form, request, 'PIN/Postcode is incorrect')

        session['authentication_attempts'] = 0  # reset attempts if successful login
        login_user(username)  # Add user to session

        # update database log information
        username.last_login = username.current_login
        username.current_login = datetime.now()
        username.total_logins += 1
        username.current_login_ip = request.remote_addr
        username.last_login_ip = username.current_login_ip
        db.session.commit()

        logging.warning('SECURITY - User logged in [%s, %s, %s]', current_user.id, current_user.email,
                        request.remote_addr)

        if current_user.role == 'admin':
            return redirect(url_for('admin.admin'))
        else:
            return redirect(url_for('lottery.lottery'))

    return render_template('users/login.html', form=form, validation_message=validation_message)


# reset authentication attempts
@users_blueprint.route('/reset')
@anonymous_required
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))


# logout user
@users_blueprint.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logging.warning('SECURITY - User logged out [%s, %s, %s]', current_user.id, current_user.email,
                        request.remote_addr)
        logout_user()

    return render_template('main/index.html')


# view user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('users/account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           date_of_birth=current_user.date_of_birth,
                           postcode=current_user.postcode,
                           phone=current_user.phone,
                           role=current_user.role)


@users_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    validation_message = ""

    if form.validate_on_submit():
        if not current_user.verify_password(form.current_password.data):
            flash('Current password is incorrect')
            return render_template('users/change_password.html', form=form, validation_message=validation_message)

        if not form.new_password.data == form.confirm_new_password.data:
            flash('New passwords do not match')
            return render_template('users/change_password.html', form=form, validation_message=validation_message)

        if current_user.verify_password(form.new_password.data):
            flash('New password cannot be the same as the current password')
            return render_template('users/change_password.html', form=form, validation_message=validation_message)

        current_user.change_password(form.new_password.data)
        db.session.commit()

        flash('Password updated successfully', 'success')

        return redirect(url_for('users.account'))

    return render_template('users/change_password.html', form=form)

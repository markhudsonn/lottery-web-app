# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_user, current_user, logout_user, login_required
from markupsafe import Markup

from app import db
from models import User
from users.forms import RegisterForm, LoginForm, ChangePasswordForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
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

        # add user to session
        session['username'] = form.email.data

        # sends user to setup 2fa page
        return redirect(url_for('users.setup_2fa'))
    # if request method is GET or form not valid re-render signup page
    return render_template('users/register.html', form=form, validation_message=validation_message)


# view 2fa setup
@users_blueprint.route('/setup_2fa', methods=['GET', 'POST'])
def setup_2fa():
    if 'username' not in session:
        return redirect(url_for('index'))

    user = User.query.filter_by(email=session['username']).first()

    if not user:
        return redirect(url_for('index'))

    del session['username']

    return render_template('users/setup_2fa.html', user=user.email, uri=user.get_2fa_uri()), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache', 'Expires': '0'}


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    validation_message = ""

    if not session.get('authentication_attempts'):
        session['authentication_attempts'] = 0

    if session['authentication_attempts'] >= 3:
        flash(Markup('Too many authentication attempts. Please click <a href="/reset">here</a> to reset'), 'danger')
        return render_template('users/login.html')

    if form.validate_on_submit():
        username = User.query.filter_by(email=form.email.data).first()
        password = form.password.data
        pin = form.pin.data

        if not username:
            session['authentication_attempts'] += 1
            validation_message = 'Username or password is incorrect'
            return render_template('users/login.html', form=form, validation_message=validation_message)

        if not User.verify_password(username, password):
            session['authentication_attempts'] += 1
            validation_message = 'Username or password is incorrect'
            return render_template('users/login.html', form=form, validation_message=validation_message)

        if not username.verify_pin(pin):
            session['authentication_attempts'] += 1
            validation_message = 'PIN or postcode is incorrect'
            return render_template('users/login.html', form=form, validation_message=validation_message)

        if not username.verify_postcode(form.postcode.data):
            session['authentication_attempts'] += 1
            validation_message = 'PIN or postcode is incorrect'
            return render_template('users/login.html', form=form, validation_message=validation_message)

        login_user(username)

        if current_user.role == 'admin':
            return redirect(url_for('admin.admin'))
        else:
            return redirect(url_for('lottery.lottery'))

    attempts_remaining = 3 - session['authentication_attempts']
    flash(f'You have {attempts_remaining} attempts remaining', 'info')

    return render_template('users/login.html', form=form, validation_message=validation_message)


# reset authentication attempts
@users_blueprint.route('/reset')
def reset():
    session['authentication_attempts'] = 0
    return redirect(url_for('users.login'))


# logout user
@users_blueprint.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
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

        current_user.password = form.new_password.data
        db.session.commit()

        flash('Password updated successfully', 'success')

        return redirect(url_for('users.account'))

    return render_template('users/change_password.html', form=form)

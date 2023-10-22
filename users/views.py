# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, session

from app import db
from models import User
from users.forms import RegisterForm, LoginForm

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
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=session['username']).first()

    if not user:
        return redirect(url_for('main.index'))

    del session['username']

    return render_template('users/setup_2fa.html', user=user.email, uri=user.get_2fa_uri()), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache', 'Expires': '0'}


# view user login
@users_blueprint.route('/login')
def login():
    form = LoginForm()
    validation_message = ""

    if form.validate_on_submit():
        return redirect(url_for('users.account'))

    return render_template('users/login.html', form=form, validation_message=validation_message)


# view user account
@users_blueprint.route('/account')
def account():
    return render_template('users/account.html',
                           acc_no="PLACEHOLDER FOR USER ID",
                           email="PLACEHOLDER FOR USER EMAIL",
                           firstname="PLACEHOLDER FOR USER FIRSTNAME",
                           lastname="PLACEHOLDER FOR USER LASTNAME",
                           phone="PLACEHOLDER FOR USER PHONE")

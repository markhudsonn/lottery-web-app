# IMPORTS
import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from flask_qrcode import QRcode
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ECHO'] = os.getenv('SQLALCHEMY_ECHO') == 'True'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')

# initialise database
db = SQLAlchemy(app)
QRcode(app)


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('main/index.html')


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return render_template('errors/403.html'), 403

            return f(*args, **kwargs)

        return wrapped

    return wrapper


# BLUEPRINTS
# import blueprints
from users.views import users_blueprint
from admin.views import admin_blueprint
from lottery.views import lottery_blueprint
from errors.views import errors_blueprint

#
# # register blueprints with app
app.register_blueprint(users_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(lottery_blueprint)
app.register_blueprint(errors_blueprint)

# initialise login manager
login_manager = LoginManager()
login_manager.login_view = 'users.views.login'
login_manager.init_app(app)

from models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run()

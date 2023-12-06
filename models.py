import pickle
from datetime import datetime

import bcrypt
import pyotp
import rsa
from flask_login import UserMixin

from app import db, app


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.BLOB, nullable=False)
    pin_key = db.Column(db.String(32), nullable=True, default=pyotp.random_base32())

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    # Log Information
    registered_on = db.Column(db.DateTime, nullable=False)
    current_login = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    current_login_ip = db.Column(db.String(100), nullable=True)
    last_login_ip = db.Column(db.String(100), nullable=True)
    total_logins = db.Column(db.Integer, nullable=False, default=0)

    # Symmetric key
    # draw_key = db.Column(db.BLOB, nullable=False)

    # Asymmetric keys
    public_draw_key = db.Column(db.BLOB, nullable=False)
    private_draw_key = db.Column(db.BLOB, nullable=False)

    # Define the relationship to Draw
    draws = db.relationship('Draw')

    def __init__(self, email, firstname, lastname, date_of_birth, postcode, phone, password, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.date_of_birth = date_of_birth
        self.postcode = postcode
        self.phone = phone
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.role = role
        self.registered_on = datetime.now()
        self.current_login = None
        self.last_login = None
        self.current_login_ip = None
        self.last_login_ip = None
        self.total_logins = 0

        # Symmetric key
        # self.draw_key = Fernet.generate_key()

        # Asymmetric keys
        public_key, private_key = rsa.newkeys(512)
        self.public_draw_key = pickle.dumps(public_key)
        self.private_draw_key = pickle.dumps(private_key)

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def get_2fa_uri(self):
        return str(pyotp.totp.TOTP(self.pin_key).provisioning_uri(name=self.email, issuer_name='Lottery App'))

    def verify_pin(self, pin):
        return pyotp.TOTP(self.pin_key).verify(pin)

    def verify_postcode(self, postcode):
        return self.postcode == postcode


class Draw(db.Model):
    __tablename__ = 'draws'

    id = db.Column(db.Integer, primary_key=True)

    # ID of user who submitted draw
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # 6 draw numbers submitted
    numbers = db.Column(db.String(100), nullable=False)

    # Draw has already been played (can only play draw once)
    been_played = db.Column(db.BOOLEAN, nullable=False, default=False)

    # Draw matches with master draw created by admin (True = draw is a winner)
    matches_master = db.Column(db.BOOLEAN, nullable=False, default=False)

    # True = draw is master draw created by admin. User draws are matched to master draw
    master_draw = db.Column(db.BOOLEAN, nullable=False)

    # Lottery round that draw is used
    lottery_round = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, numbers, master_draw, lottery_round):
        self.user_id = user_id
        self.numbers = numbers
        self.been_played = False
        self.matches_master = False
        self.master_draw = master_draw
        self.lottery_round = lottery_round

    # view draw with symmetric key
    # def view_draw(self, draw_key):
    #     self.numbers = decrypt(self.numbers, draw_key)

    # view draw with asymmetric key
    def view_draw(self, private_key):
        private_key = pickle.loads(private_key)
        self.numbers = rsa.decrypt(self.numbers, private_key).decode('utf-8')


# encrypt date with symmetric key
# def encrypt(data, key):
#     return Fernet(key).encrypt(data.encode('utf-8'))


# decrypt data with symmetric key
# def decrypt(data, key):
#     return Fernet(key).decrypt(data).decode('utf-8')

# encrypt data with asymmetric key
def encrypt(data, public_key):
    public_key = pickle.loads(public_key)
    return rsa.encrypt(data.encode('utf-8'), public_key)


# decrypt data with asymmetric key
def decrypt(data, private_key):
    private_key = pickle.loads(private_key)
    return rsa.decrypt(data, private_key).decode('utf-8')


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(email='admin@email.com',
                     password='Admin1!',
                     firstname='Alice',
                     lastname='Jones',
                     date_of_birth='01/01/2000',
                     postcode='NE1 7RU',
                     phone='1234-123-1234',
                     role='admin',
                     )

        db.session.add(admin)
        db.session.commit()

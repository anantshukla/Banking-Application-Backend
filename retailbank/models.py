import flask
from retailbank import db

############### Creating database model ###########################

class Userstore(db.Model):
    login_id=db.Column(db.Integer, primary_key=True)
    password=db.Column(db.String(45),unique=False, nullable=False)
    time = db.Column(db.String(120), unique=False,nullable=False)
    token = db.Column(db.String(200),unique=True,nullable=True)
    user_role = db.Column(db.String(10),unique=False,nullable=False)
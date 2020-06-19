from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import logging

app = Flask(__name__)
app.config.from_object(Config)

################ configuring Database ##############################
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Aatikyakhandala1@@localhost/retail_bank'
db=SQLAlchemy(app)
ma = Marshmallow(app)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

from retailbank import route
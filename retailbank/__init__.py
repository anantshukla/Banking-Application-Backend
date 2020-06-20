from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config.from_object(Config)

################ configuring Database ##############################
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tcscasestudy@retail-bankdbserver:Aatikyakhandala1@@bankdbserver.mysql.database.azure.com/retail_bank'  # Please change according to your system
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{hostname}/{databasename}".format(
username="tcscasestudy@retail-bankdbserver",
password="Aatikyakhandala1@",
hostname="retail-bankdbserver.mysql.database.azure.com",
databasename="retail_bank",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'mySecretKey' 
db=SQLAlchemy(app)
ma = Marshmallow(app)



from retailbank import route
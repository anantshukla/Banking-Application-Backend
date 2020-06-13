from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(Config)

################ configuring Database ##############################
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Aatikyakhandala1@@localhost/retail_bank'
db=SQLAlchemy(app)



from retailbank import route
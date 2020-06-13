from flask import Flask,jsonify,request
from retailbank import app,db
from retailbank.models import Userstore
import datetime
import uuid

########### Login API    ##############

@app.route("/login",methods=["POST"])
def login():
    data = request.get_json()
    username=int(data["username"])
    password=data["password"]
    user = Userstore.query.filter_by(login_id=username,password=password).first()   #checking credencial
    if user:
        if user.token=="" or user.token==None:    #checking if user if login first time
            token=uuid.uuid4()   #generating token and storing into database
            user.token=str(token)
            db.session.commit()
            return jsonify({"status":True,"role":user.user_role,"token":token})    #reponding with user role and token
        else:
            return jsonify({"status":True,"role":user.user_role,"token":user.token})   
    else:
        return jsonify({"error":"failed"}),401      #responding with error 401
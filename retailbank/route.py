from flask import Flask,jsonify,request
from retailbank import app,db
from retailbank.models import Userstore, Customer, Customer_status,customer_schema
import datetime
import uuid

########### Login API    ##############

@app.route("/login",methods=["POST"])
def login():
    data = request.get_json()
    username=int(data["username"])
    password=data["password"]
    user = Userstore.query.filter_by(login_id=username,password=password).first()   # checking credencial
    if user:
        if user.token=="" or user.token==None:    # checking if user if login first time
            token=uuid.uuid4()  # generating token and storing into database
            user.token=str(token)
            db.session.commit()
            return jsonify({"status":True,"role":user.user_role,"token":token})    # reponding with user role and token
        else:
            return jsonify({"status":True,"role":user.user_role,"token":user.token})   
    else:
        return jsonify({"status":False,"message":"Something went wrong! Please check your credential"})     #responding with error

############# API for creating Customer #################

@app.route("/createcustomer", methods=["POST"])
def createcustomer():
    data = request.get_json()
    token = data["token"]
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            ssn = data["ssn"]
            if Customer.query.filter_by(ws_ssn=ssn).first():    # Checking for duplicate ssn
                return jsonify({"status":False,"messaage":f"Customer with ssn {ssn} already exist"})
            cust_id = Customer.query.count()+1
            name = data["name"]
            age = data["age"]
            address = data["address"]+","+data["city"]+","+data["state"]
            cust = Customer(ws_ssn=ssn,ws_cust_id=cust_id,ws_name=name,ws_adrs=address,ws_age=age)
            db.session.add(cust)        # Saving customer in database
            cust_status_index = Customer_status.query.count()+1
            cust_status = Customer_status(ws_ssn=ssn, ws_cust_id=cust_id, ws_status=1, ws_msg="Customer created successfully",
            ws_lup=datetime.datetime.now(), cust_status_index=cust_status_index)
            db.session.add(cust_status)     # Saving customer status in database
            db.session.commit()
            return jsonify({"status":True,"message":"Customer created successfully"})
        return jsonify({'status':False,'message':'Not authorized'})
    return jsonify({'status':False,'message':'Not authenticated'})

###############  API for customer search ##################

@app.route("/customersearch", methods=["POST"])
def customersearch():
    data = request.get_json()
    token = data["token"]
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if data.get('type')=='ssn':         # Checking search type
                customer = Customer.query.filter_by(ws_ssn=int(data.get('id'))).first() # Query to featch data
                result = customer_schema.dump(customer)     # Serializing the database result
                return jsonify({"status":True, "result":result})
            customer = Customer.query.filter_by(ws_cust_id=int(data.get('id'))).first()
            result = customer_schema.dump(customer)
            return jsonify({"status":True, "result":result})
        return jsonify({'status':False,'message':'Not authorized'})            
    return jsonify({'status':False,'message':'Not authenticated'})


@app.route("/customerupdate", methods=["POST"])
def customerupdate():
    data = request.get_json()
    token = data["token"]
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            customer = Customer.query.filter_by(ws_cust_id=data.get('ws_cust_id')).first()
            customer.ws_name=data.get('ws_name')
            customer.ws_age=data.get('ws_age')
            customer.ws_adrs=data.get('ws_adrs')    # Updating customer details
            cust_status_index = Customer_status.query.count()+1
            cust_status = Customer_status(ws_ssn=data.get('ws_ssn'), ws_cust_id=data.get('ws_cust_id'), ws_status=1, ws_msg="Customer update complete",
            ws_lup=datetime.datetime.now(), cust_status_index=cust_status_index)
            db.session.add(cust_status)     # Creating customer status
            db.session.commit()     
            return jsonify({"status":True,"messgae":"Customer update complete"})
        return jsonify({'status':False,'message':'Not authorized'})            
    return jsonify({'status':False,'message':'Not authenticated'})








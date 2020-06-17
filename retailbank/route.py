from flask import Flask,jsonify,request
from retailbank import app,db
from retailbank.models import Userstore, Customer, account_status_schema, transcation_schema, Customer_status, account_schema, accounts_schema, customer_schema, customer_status_schema, Account, Account_status, Transcation
import datetime
import uuid
from sqlalchemy import desc


########### Login API    ##############

@app.route("/login",methods=["POST"])
def login():
    # data = request.get_json()
    username=int(request.form.get('username'))
    password=request.form.get('password')
    user = Userstore.query.filter_by(login_id=username,password=password).first()   # checking credencial
    if user:
        if user.token=="" or user.token==None:    # checking if user if login first time
            token=uuid.uuid4()  # generating token and storing into database
            user.token=str(token)
            db.session.commit()
            return jsonify({"status":True,"role":user.user_role,"token":token})    # reponding with user role and token
        
        return jsonify({"status":True,"role":user.user_role,"token":user.token})   
    
    return jsonify({"status":False,"message":"Something went wrong! Please check your credential"})     #responding with error

############# API for creating Customer #################

@app.route("/createcustomer", methods=["POST"])
def createcustomer():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            ssn = request.form.get('ssn')
            if Customer_status.query.filter_by(ws_ssn=ssn,ws_status="Deactive").first():    # Checking for duplicate ssn
                customer = Customer_status.query.filter_by(ws_ssn=ssn).first()
                customer.ws_status='Active'
                customer.ws_msg="Customer reactivate success"
                customer.ws_lup=datetime.datetime.now()
                db.session.commit()
                return jsonify({"status":True,"message":f"Customer with ssn {ssn} reactivated successfully"})

            if Customer_status.query.filter_by(ws_ssn=ssn,ws_status="Active").first():  
                return jsonify({'status':False,'message':f"Customer with id {ssn} already exist"})
            
            cust_id = Customer.query.count()+100000000
            name = request.form.get('name')
            age = request.form.get('age')
            address = request.form.get('address')+","+request.form.get('city')+","+request.form.get('state')
            cust = Customer(ws_ssn=ssn,ws_cust_id=cust_id,ws_name=name,ws_adrs=address,ws_age=age)
            db.session.add(cust)        # Saving customer in database
            cust_status_index = Customer_status.query.count()+100000000
            cust_status = Customer_status(ws_ssn=ssn, ws_cust_id=cust_id, ws_status="Active", ws_msg="Customer created successfully",
            ws_lup=datetime.datetime.now(), cust_status_index=cust_status_index)
            db.session.add(cust_status)     # Saving customer status in database
            db.session.commit()
            return jsonify({"status":True,"message":f"Customer with id {cust_id} created successfully"})
        
        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

###############  API for customer search ##################

@app.route("/customersearch", methods=["POST"])
def customersearch():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if request.form.get('type')=='ssn':         # Checking search type
                if request.form.get('id')=="":
                    return jsonify({'status':False,'message':"SSN field can not be empty."})
                customer = Customer.query.filter_by(ws_ssn=int(request.form.get('id'))).first() # Query to featch data
                if customer:    # Checking whether ssn is valid or not
                    if Customer_status.query.filter_by(ws_ssn=customer.ws_ssn,ws_status='Active').first():   # Checking customer status
                        result = customer_schema.dump(customer)     # Serializing the database result
                        return jsonify({"status":True, "result":result})
                    
                    return jsonify({'status':False,"message":f"Customer with ssn {request.form.get('id')} is deactivated"})    
                
                return jsonify({"status":False,"message":f"Customer with ssn {request.form.get('id')} does not exist"})        
            
            if request.form.get('id')=="":
                return jsonify({'status':False,'message':"Customer id field can not be empty."})

            customer = Customer.query.filter_by(ws_cust_id=int(request.form.get('id'))).first()
            if customer:        # Checking whether customer id is valid or not
                if Customer_status.query.filter_by(ws_ssn=customer.ws_ssn,ws_status='Active').first():
                    result = customer_schema.dump(customer)
                    return jsonify({"status":True, "result":result})
                
                return jsonify({'status':False,"message":f"Customer with id {request.form.get('id')} is deactivated"})    
    
            return jsonify({"status":False,"message":f"Customer with id {request.form.get('id')} does not exist"})    
        
        return jsonify({'status':False,'message':'Not authorized'})            
   
    return jsonify({'status':False,'message':'Not authenticated'})


########### API for customer updation ###############

@app.route("/customerupdate", methods=["POST"])
def customerupdate():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if request.form.get("ws_name")=="" and request.form.get('ws_age')=="" and request.form.get('ws_adrs')=="":
                return jsonify({"status":False,"message":"Please give data for atleast one field"})
            
            customer = Customer.query.filter_by(ws_cust_id=request.form.get('ws_cust_id')).first()
            if customer:
                if Customer_status.query.filter_by(ws_ssn=customer.ws_ssn,ws_status='Active').first():   # Checking customer status
                    if request.form.get('ws_name')!="":
                        customer.ws_name=request.form.get('ws_name')
                    if request.form.get('ws_age')!="":    
                        customer.ws_age=request.form.get('ws_age')
                    if request.form.get('ws_adrs')!="":
                        customer.ws_adrs=request.form.get('ws_adrs')    # Updating customer details
                    cust_status = Customer_status.query.filter_by(ws_cust_id=request.form.get('ws_cust_id')).first()
                    cust_status.ws_msg = "Customer update complete"     # Updating customer status message
                    cust_status.ws_lup = datetime.datetime.now()        # Updating Customer Last update time
                    db.session.commit()     
                    return jsonify({"status":True,"message":"Customer update complete"})

                return jsonify({'status':False,'message':f"Customer with ssn {request.form.get('ws_ssn')} is deactivated"})

            return jsonify({'status':False,'message':f"Customer with id {request.form.get('ws_cust_id')} doesn't exist"})

        return jsonify({'status':False,'message':'Not authorized'})            
    
    return jsonify({'status':False,'message':'Not authenticated'})


############# API for Customer deletion #################

@app.route("/customerdelete", methods=["POST"])
def deletecustomer():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if not Customer.query.filter_by(ws_ssn=request.form.get('ws_ssn')).first():
                return jsonify({'status':False,'message':f"Customer with id {request.form.get('ws_ssn')} doesn't exist"})
            if Customer_status.query.filter_by(ws_ssn=request.form.get('ws_ssn')).first().ws_status=='Deactive':      # Checking customer status
                return jsonify({'status':False,'message':f"Customer with usn {request.form.get('ws_ssn')} is already deactive"})
            
            customer = Customer_status.query.filter_by(ws_ssn=request.form.get('ws_ssn')).first()
            customer.ws_status = "Deactive"         # Changing status from Active to Deactive
            cust_detail = Customer.query.filter_by(ws_ssn=request.form.get('ws_ssn')).first()
            acct_details = Account_status.query.filter_by(ws_cust_id=cust_detail.ws_cust_id).all()
            customer.ws_msg = "Customer delete complete"     # Updating customer status message
            customer.ws_lup = datetime.datetime.now()        # Updating Customer Last update time
            if acct_details:
                for acct in acct_details:
                    acct.ws_status="Deactive"
            db.session.commit() 
            return jsonify({"status":True, "message":f"Customer with ssn {request.form.get('ws_ssn')} is deleted"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

############ API for customer reactivation ################

@app.route("/customerreactivate", methods=["POST"])
def customerreactivate():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if not Customer.query.filter_by(ws_ssn=request.form.get('ws_ssn')).first():
                return jsonify({'status':False,'message':f"Customer with id {request.form.get('ws_ssn')} doesn't exist"})
            if Customer_status.query.filter_by(ws_ssn=request.form.get('ws_ssn')).first().ws_status=='Active':    # Checking customer status
                return jsonify({'status':False,'message':f"Customer with usn {request.form.get('ws_ssn')} is already active"})
            
            customer = Customer_status.query.filter_by(ws_ssn=request.form.get('ws_ssn')).first()
            customer.ws_status = 'Active'
            customer.ws_msg = "Customer reactivation complete"
            customer.ws_lup = datetime.datetime.now()
            db.session.commit() 
            return jsonify({"status":True, "message":f"Customer with ssn {request.form.get('ws_ssn')} is reactivated"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

########### API for customer status ##############

@app.route("/customerstatus", methods=["POST"])
def customerstatus():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            cust_status = Customer_status.query.all()
            if cust_status:
                result = customer_status_schema.dump(cust_status)    # Serializing database objects
                return jsonify({'status':True,'result':result})

            return jsonify({'status':False, 'message':"There is not customer currently"})    

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

########## API for deactive customer status ##############

@app.route("/customersearchdistint", methods=["POST"])
def customersearchdistint():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            cust_status = Customer_status.query.group_by(Customer_status.ws_ssn).distinct(Customer_status.ws_ssn).filter_by(ws_status="Deactive").all()
            if cust_status:
                result = customer_status_schema.dump(cust_status)    # Serializing database objects
                return jsonify({'status':True,'result':result})

            return jsonify({'status':False, 'message':"There is no deactivate Customer currently"})    
    

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})






############## API for account create  #################

@app.route("/accountcreate", methods=["POST"])
def accountcreate():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if not Customer.query.filter_by(ws_cust_id=request.form.get('ws_cust_id')).first():
                return jsonify({'status':False,'message':f"Customer with id {request.form.get('ws_cust_id')} doesn't exist"})
            if request.form.get('ws_acct_type') =='Saving' or request.form.get('ws_acct_type') =='saving':
                account_type = 's'
            else:
                account_type = 'c' 

            if Account_status.query.filter_by(ws_cust_id=request.form.get('ws_cust_id'),ws_acct_type=account_type,ws_status="Deactive").first():
                acct = Account_status.query.filter_by(ws_cust_id=request.form.get('ws_cust_id'),ws_acct_type=account_type).first()
                acct.ws_status="Active"
                acct.ws_cust_msg = "Account Activated"
                acct.ws_lup = datetime.datetime.now()
                db.session.commit()
                return jsonify({'status':True,'message':"Account reactivated successfully"})

            if Account.query.filter_by(ws_cust_id=request.form.get('ws_cust_id'),ws_acct_type=account_type).first():   # Checking if for requested account is already exist with customer    
                return jsonify({'status':False,'message':f"Customer with id {request.form.get('ws_cust_id')} already has {request.form.get('ws_acct_type')} account"})    # Returning the error message

            if request.form.get('ws_acct_balance') =="":
                return jsonify({'status':False, 'message':'Balnace field can not be empty'})

            if Customer_status.query.filter_by(ws_cust_id=request.form.get('ws_cust_id'),ws_status="Active").first():    
                ac_id = Account.query.count()+100000000
                account = Account(ws_cust_id=request.form.get('ws_cust_id'),ws_acct_id=ac_id,ws_acct_type=account_type,ws_acct_balance=float(request.form.get('ws_acct_balance')),
                ws_acct_crdate=datetime.datetime.now(), ws_acct_lasttrdate=datetime.datetime.now(),ws_acct_duration=0)   # Creating the Account
                db.session.add(account)
                account_status_id = Account_status.query.count()+100000000
                account_status = Account_status(ws_cust_id=request.form.get('ws_cust_id'),ws_acct_id=ac_id,ws_acct_type=account_type,
                ws_status='Active',ws_cust_msg='Account created succesfully',ws_cust_lup=datetime.datetime.now(),acct_status_index=account_status_id)  # Making entry in Account status table
                db.session.add(account_status)
                db.session.commit()
                return jsonify({'status':True,'message':f"Account with id {ac_id} created successfully"})

            return jsonify({'status':False,'message':f"Customer with id {request.form.get('ws_cust_id')} is Deactive, Please request for Activation."})    

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


########### API for account search ################

@app.route("/accountsearch", methods=["POST"])
def accountsearch():
    token = request.form.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role == "teller" or user.user_role =='account executive':    # Checking authorization with user_role
            if request.form.get('type')=='accountid':         # Checking search type
                if Account.query.filter_by(ws_acct_id=request.form.get('id')).first():   # Checking whether Account with given id exists or not
                    account = Account.query.filter_by(ws_acct_id=int(request.form.get('id'))).first() # Query to featch data
                    result = account_schema.dump(account)     # Serializing the database result
                    if result['ws_acct_type'] =='s':
                        result['ws_acct_type'] ="Saving"
                    else:
                        result['ws_acct_type']= "Current"    
                    return jsonify({"status":True, "result":result})

                return jsonify({'status':False,'message':f"Account with id {request.form.get('id')} doesn't exist"})    
            
            if Account.query.filter_by(ws_cust_id=int(request.form.get('id'))).first():     # Checking whether Customer with given id exists or not
                account = Account.query.filter_by(ws_cust_id=int(request.form.get('id'))).all()
                result = accounts_schema.dump(account)
                for res in result:
                    if res['ws_acct_type'] =='s':
                        res['ws_acct_type'] ="Saving"
                    else:
                        res['ws_acct_type']= "Current" 
                return jsonify({"status":True, "result":result})

            return jsonify({'status':False,'message':f"Customer wih id {request.form.get('id')} doesn't exist"})

        return jsonify({'status':False,'message':'Not authorized'})   

    return jsonify({'status':False,'message':'Not authenticated'})

############ API for account delete ##################

@app.route("/accountdelete", methods=["POST"])
def accountdelete():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            account =Account_status.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first()
            if account:
                if account.ws_status=='Deactive':      # Checking account status
                    return jsonify({'status':False,'message':f"Account with id {request.form.get('ws_acct_id')} is already deactive"})

                account.ws_status = "Deactive"         # Changing status from Active to Deactive
                account.ws_cust_msg = "Account deleted successfully"
                account.ws_cust_lup = datetime.datetime.now() 
                db.session.commit() 
                return jsonify({"status":True, "message":f"Account with id {request.form.get('ws_acct_id')} is deleted"})

            return jsonify({'status':False,'message':f"Account with id {request.form.get('ws_acct_id')} doesn't exist"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


############ API for account reactivation ###############

@app.route("/accountreactivate", methods=["POST"])
def accountreactivate():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if not Account.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first():
                return jsonify({'status':False,'message':f"Account with id {request.form.get('ws_acct_id')} doesn't exist"})
            if Account_status.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first().ws_status=='Active':    # Checking customer status
                return jsonify({'status':False,'message':f"Account with id {request.form.get('ws_acct_id')} is already active"})
            
            account = Account_status.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first()
            account.ws_status = "Active"     # Changing status from Deactive to Active
            account.ws_cust_msg = "Account reactivated successfully"
            account.ws_cust_lup = datetime.datetime.now()
            db.session.commit() 
            return jsonify({"status":True, "message":f"Account with id {request.form.get('ws_acct_id')} is reactivated"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

############ API for distinct account search ###############

@app.route("/accountsearchdistint", methods=["POST"])
def accountsearchdistint():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            acct_status = Account_status.query.group_by(Account_status.ws_acct_id).distinct(Account_status.ws_acct_id).filter_by(ws_status="Deactive").all()
            if acct_status:
                result = account_status_schema.dump(acct_status)    # Serializing database objects
                for res in result:
                    if res['ws_acct_type'] =='s':
                        res['ws_acct_type'] ="Saving"
                    else:
                        res['ws_acct_type']= "Current" 
                return jsonify({'status':True,'result':result})

            return jsonify({'status':False, 'message':"There is no deactivate account currently"})    

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

############# API for account status ###############

@app.route("/accountstatus", methods=["POST"])
def accountstatus():
    token = request.form.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            acct_status = Account_status.query.all()
            result = account_status_schema.dump(acct_status)    # Serializing database objects
            for res in result:
                if res['ws_acct_type'] =='s':
                    res['ws_acct_type'] ="Saving"
                else:
                    res['ws_acct_type']= "Current" 
            return jsonify({'status':True,'result':result})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


############ API for deposit amount ################

@app.route("/deposite", methods=["POST"])
def deposit():
    token = request.form.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if not Account.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first():
                return jsonify({'status':False,'message':f"Account with id {request.form.get('ws_acct_id')} doesn't exist"})

            if float(request.form.get('amount'))<=0:
                return jsonify({'status':False, 'message':'Amount must be grether than 0'})
            if Account_status.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first().ws_status=='Deactive':
                return jsonify({'status':False, 'message':f"Account with id {request.form.get('ws_acct_id')} is deactive please request for reactivation."})

            acct_details = Account.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first()
            acct_details.ws_acct_balance += float(request.form.get('amount'))
            tranx_id = Transcation.query.count()+100000000
            transcation = Transcation(ws_cust_id=acct_details.ws_cust_id, ws_acct_type=acct_details.ws_acct_type, ws_amt=float(request.form.get('amount')),
            ws_trxn_date=datetime.datetime.now(), ws_src_typ='d', ws_tgt_typ=acct_details.ws_acct_type, trxn_id= tranx_id,description="Deposite")
            db.session.add(transcation)
            db.session.commit() 
            return jsonify({'status':True, 'balance':acct_details.ws_acct_balance})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


############ API for withdraw ##############

@app.route("/withdraw", methods=["POST"])
def withdraw():
    token = request.form.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if not Account.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first():
                return jsonify({'status':False,'message':f"Account with id {request.form.get('ws_acct_id')} doesn't exist"})
            if float(request.form.get('amount'))<=0:
                return jsonify({'status':False, 'message':'Amount must be grether than 0'})
            if Account_status.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first().ws_status=='Deactive':
                return jsonify({'status':False, 'message':f"Account with id {request.form.get('ws_acct_id')} is deactive please request for reactivation."})


            account = Account.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first()
            if account.ws_acct_type=='s':
                if account.ws_acct_balance-float(request.form.get('amount'))>=0:
                    account.ws_acct_balance -= float(request.form.get('amount'))
                    tranx_id = Transcation.query.count()+100000000
                    transcation = Transcation(ws_cust_id=account.ws_cust_id, ws_acct_type=account.ws_acct_type, ws_amt=float(request.form.get('amount')),
                    ws_trxn_date=datetime.datetime.now(), ws_src_typ=account.ws_acct_type, ws_tgt_typ='w', trxn_id= tranx_id,description="Withdraw")
             
                    db.session.add(transcation)
                    db.session.commit()
                    return jsonify({'status':True, 'balance':account.ws_acct_balance})

                return jsonify({'status':False, 'message':"Insufficient balance"}) 

            if account.ws_acct_type=='c':
                if account.ws_acct_balance-float(request.form.get('amount'))>=-5000:
                    account.ws_acct_balance -= float(request.form.get('amount'))
                    tranx_id = Transcation.query.count()+100000000
                    transcation = Transcation(ws_cust_id=account.ws_cust_id, ws_acct_type=account.ws_acct_type, ws_amt=float(request.form.get('amount')),
                    ws_trxn_date=datetime.datetime.now(), ws_src_typ=account.ws_acct_type, ws_tgt_typ='w', trxn_id= tranx_id,description="Withdraw")
                   
                    db.session.add(transcation)
                    db.session.commit()
                    return jsonify({'status':True, 'balance':account.ws_acct_balance})

                return jsonify({'status':False, 'message':"Insufficient balance"})   
   
        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


########### API for transfer money ###############
@app.route("/transfer", methods=["POST"])
def transfer():
    token = request.form.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if not Customer.query.filter_by(ws_cust_id=request.form.get('ws_cust_id')).first():
                return jsonify({'status':False,'message':f"Customer with id {request.form.get('ws_cust_id')} doesn't exist"})

            if request.form.get('amount')=="":
                return jsonify({'status':False, 'message':'Please fill the amount field'})

            if float(request.form.get('amount'))<=0:
                return jsonify({'status':False,'message':'Amount must be grether than 0'})    

            if Customer_status.query.filter_by(ws_cust_id=request.form.get('ws_cust_id')).first().ws_status=='Deactive':
                return jsonify({'status':False, 'message':f"Customer with id {request.form.get('ws_cust_id')} is deactive please request for reactivation."})

            if Account_status.query.filter_by(ws_cust_id=request.form.get('ws_cust_id'), ws_acct_type='s', ws_status='Active').first():        # Checking if customer has saving account
                if Account_status.query.filter_by(ws_cust_id=request.form.get('ws_cust_id'), ws_acct_type='c', ws_status='Active').first():    # Checking if customer has current account
                    if request.form.get('ws_src_type') =="Saving" or request.form.get('ws_src_type')=="saving":
                        src_type="s"
                    else:
                        src_type="c"    
                    if request.form.get('ws_trg_type')=="Current" or request.form.get('ws_trg_type')=="current":
                        trg_type = 'c'
                    else:
                        trg_type='s'    
                    if src_type==trg_type:
                        return jsonify({'status':False,'message':"Both account type can not be same"})  

                    if src_type =='s':                                                              # Checking if source account is saving
                        saving_account = Account.query.filter_by(ws_acct_type=src_type).first()
                        current_account = Account.query.filter_by(ws_acct_type=trg_type).first()
                        if saving_account.ws_acct_balance-float(request.form.get('amount'))>=0:             # Checking if transfering amount available in account
                            saving_account.ws_acct_balance -= float(request.form.get('amount'))             # Deducting amount from saving account
                            current_account.ws_acct_balance += float(request.form.get('amount'))            # Credicting amount in current account
                            tranx_id1 = Transcation.query.count()+100000000
                            transcation1 = Transcation(ws_cust_id=saving_account.ws_cust_id, ws_acct_type=src_type, ws_amt=float(request.form.get('amount')),
                            ws_trxn_date=datetime.datetime.now(), ws_src_typ=src_type, ws_tgt_typ=trg_type, trxn_id= tranx_id1,description="Transfer")
                            db.session.add(transcation1)        # Adding entry for saving account in Transaction table
                            db.session.commit()


                            tranx_id2 = Transcation.query.count()+100000000
                            transcation2 = Transcation(ws_cust_id=current_account.ws_cust_id, ws_acct_type=trg_type, ws_amt=float(request.form.get('amount')),
                            ws_trxn_date=datetime.datetime.now(), ws_src_typ=src_type, ws_tgt_typ=trg_type, trxn_id= tranx_id2,description="Transfer")
                            db.session.add(transcation2)        # Adding entry for current account in Transaction table
                            db.session.commit()
                            return jsonify({'status':True, 'message':"Transfer completed",'current_amount':current_account.ws_acct_balance,'saving_amount':saving_account.ws_acct_balance})

                        return jsonify({'status':False, 'message':"Insufficient balance"})

                    saving_account = Account.query.filter_by(ws_acct_type=trg_type, ws_cust_id=request.form.get('ws_cust_id')).first()
                    current_account = Account.query.filter_by(ws_acct_type=src_type, ws_cust_id=request.form.get('ws_cust_id')).first()
                    if current_account.ws_acct_balance-float(request.form.get('amount'))>=-5000:        # Checking if requested amount fell under overdraft amount or not
                        current_account.ws_acct_balance -= float(request.form.get('amount'))            # Deducting money from current account
                        saving_account.ws_acct_balance += float(request.form.get('amount'))             # Credicting money in saving account
                        tranx_id1 = Transcation.query.count()+100000000
                        transcation1 = Transcation(ws_cust_id=current_account.ws_cust_id, ws_acct_type=src_type, ws_amt=float(request.form.get('amount')),
                        ws_trxn_date=datetime.datetime.now(), ws_src_typ=src_type, ws_tgt_typ=trg_type, trxn_id= tranx_id1,description="Transfer")
                        db.session.add(transcation1)            # Adding entry for current account
                        db.session.commit()


                        tranx_id2 = Transcation.query.count()+100000000
                        transcation2 = Transcation(ws_cust_id=current_account.ws_cust_id, ws_acct_type=trg_type, ws_amt=float(request.form.get('amount')),
                        ws_trxn_date=datetime.datetime.now(), ws_src_typ=src_type, ws_tgt_typ=trg_type, trxn_id= tranx_id2,description="Transfer")
                        db.session.add(transcation2)            # Adding entry for saving account
                        db.session.commit()
                        return jsonify({'status':True, 'message':"Transfer completed",'current_amount':current_account.ws_acct_balance,'saving_amount':saving_account.ws_acct_balance})

                    return jsonify({'status':False, 'message':"Insufficient balance"})

                   
                return jsonify({'status':False, 'message':f"Customer with id {request.form.get('ws_cust_id')} doesn't have current account or account is deactivated"})
           
            return jsonify({'status':False, 'message':f"Customer with id {request.form.get('ws_cust_id')} doesn't have Saving account or account is deactivated"})
        
        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


############ API for Transaction ###############

@app.route("/transactionhistory", methods=["POST"])    
def transactionhistory():
    token = request.form.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if not Account.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first():
                return jsonify({'status':False,'message':f"Account with id {request.form.get('ws_acct_id')} doesn't exist"})
           
            if Account_status.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first().ws_status=="Active":
                acct = Account.query.filter_by(ws_acct_id=request.form.get('ws_acct_id')).first()
                cust_id = acct.ws_cust_id
                acct_type = acct.ws_acct_type
                if request.form.get('type')=="no":
                    totaltransaction = int(request.form.get('number'))
                    trax_details = Transcation.query.filter_by(ws_cust_id=cust_id,ws_acct_type=acct_type).order_by(Transcation.trxn_id).limit(totaltransaction)
                    result = transcation_schema.dump(trax_details)
                    final_result = []
                    for res in result:
                        del(res['ws_cust_id'],res['ws_acct_type'],res['ws_src_typ'],res['ws_tgt_typ'])
                        final_result.append(res)
                    return jsonify({'status':True,'result':result})

                fromdate = request.form.get('from')
                todate = request.form.get('to')
                format_str = '%m/%d/%Y'
                fromdate_obj = datetime.datetime.strptime(fromdate, format_str)
                todate_obj = datetime.datetime.strptime(todate,format_str)
                trax_details = Transcation.query.filter_by(ws_cust_id=cust_id,ws_acct_type=acct_type).all()
                result = transcation_schema.dump(trax_details)
                final_result =[]
                for res in result:
                    if res['ws_trxn_date'] >=str(fromdate_obj.date()) and res['ws_trxn_date'] <=str(todate_obj.date()):
                        del(res['ws_cust_id'],res['ws_acct_type'],res['ws_src_typ'],res['ws_tgt_typ'])
                        final_result.append(res)
                if len(final_result)==0:
                    return jsonify({'status':False,'message':f"No transaction fall between {fromdate_obj.date()} and {todate_obj.date()}."})        
                return jsonify({'status':True,'result':final_result})

            return jsonify({'status':False,'message':f"Account with id {request.form.get('ws_acct_id')} is deactivated, Please request for reactivation."})    


        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})
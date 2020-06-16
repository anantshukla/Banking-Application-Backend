from flask import Flask,jsonify,request
from retailbank import app,db
from retailbank.models import Userstore, Customer, account_status_schema, transcation_schema, Customer_status, account_schema, accounts_schema, customer_schema, customer_status_schema, Account, Account_status, Transcation
import datetime
import uuid

########### Login API    ##############

@app.route("/login",methods=["POST"])
def login():
    data = request.get_json()
    username=int(data.get('username'))
    password=data.get('password')
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
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            ssn = data.get('ssn')
            if Customer.query.filter_by(ws_ssn=ssn).first():    # Checking for duplicate ssn
                return jsonify({"status":False,"messaage":f"Customer with ssn {ssn} already exist"})
            
            cust_id = Customer.query.count()+100000000
            name = data.get('name')
            age = data.get('age')
            address = data.get('address')+","+data.get('city')+","+data.get('state')
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
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if data.get('type')=='ssn':         # Checking search type
                customer = Customer.query.filter_by(ws_ssn=int(data.get('id'))).first() # Query to featch data
                if customer:    # Checking whether ssn is valid or not
                    if Customer_status.query.filter_by(ws_ssn=customer.ws_ssn,ws_status='Active').first():   # Checking customer status
                        result = customer_schema.dump(customer)     # Serializing the database result
                        return jsonify({"status":True, "result":result})
                    
                    return jsonify({'status':False,"message":f"Customer with ssn {data.get('id')} is deactivated"})    
                
                return jsonify({"status":False,"message":f"Customer with ssn {data.get('id')} does not exist"})        
            
            customer = Customer.query.filter_by(ws_cust_id=int(data.get('id'))).first()
            if customer:        # Checking whether customer id is valid or not
                if Customer_status.query.filter_by(ws_ssn=customer.ws_ssn,ws_status='Active').first():
                    result = customer_schema.dump(customer)
                    return jsonify({"status":True, "result":result})
                
                return jsonify({'status':False,"message":f"Customer with id {data.get('id')} is deactivated"})    
    
            return jsonify({"status":False,"message":f"Customer with id {data.get('id')} does not exist"})    
        
        return jsonify({'status':False,'message':'Not authorized'})            
   
    return jsonify({'status':False,'message':'Not authenticated'})


########### API for customer updation ###############

@app.route("/customerupdate", methods=["POST"])
def customerupdate():
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if data.get("ws_name")=="" and data.get('ws_age')=="" and data.get('ws_adrs')=="":
                return jsonify({"status":False,"messgae":"Please give data for atleast one field"})
            
            customer = Customer.query.filter_by(ws_cust_id=data.get('ws_cust_id')).first()
            if Customer_status.query.filter_by(ws_ssn=customer.ws_ssn,ws_status='Active').first():   # Checking customer status
                if data.get('ws_name')!="":
                    customer.ws_name=data.get('ws_name')
                if data.get('ws_age')!="":    
                    customer.ws_age=data.get('ws_age')
                if data.get('ws_adrs')!="":
                    customer.ws_adrs=data.get('ws_adrs')    # Updating customer details
                cust_status_index = Customer_status.query.count()+100000000
                cust_status = Customer_status(ws_ssn=data.get('ws_ssn'), ws_cust_id=data.get('ws_cust_id'), ws_status="Active", ws_msg="Customer update complete",
                ws_lup=datetime.datetime.now(), cust_status_index=cust_status_index)
                db.session.add(cust_status)     # Creating customer status
                db.session.commit()     
                return jsonify({"status":True,"messgae":"Customer update complete"})

            return jsonify({'status':False,'message':f"Customer with ssn {data.get('ws_ssn')} is deactivated"})

        return jsonify({'status':False,'message':'Not authorized'})            
    
    return jsonify({'status':False,'message':'Not authenticated'})


############# API for Customer deletion #################

@app.route("/customerdelete", methods=["POST"])
def deletecustomer():
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if Customer_status.query.filter_by(ws_ssn=data.get('ws_ssn')).first().ws_status=='Deactive':      # Checking customer status
                return jsonify({'status':False,'message':f"Customer with usn {data.get('ws_ssn')} is already deactive"})
            
            customer = Customer_status.query.filter_by(ws_ssn=data.get('ws_ssn')).all()
            for cust in customer:
                cust.ws_status = "Deactive"         # Changing status from Active to Deactive
            cust_status_index = Customer_status.query.count()+100000000
            cust_detail = Customer.query.filter_by(ws_ssn=data.get('ws_ssn')).first()
            cust_status = Customer_status(ws_ssn=data.get('ws_ssn'), ws_cust_id=cust_detail.ws_cust_id, ws_status="Deactive", ws_msg="Customer deleted successfully",
            ws_lup=datetime.datetime.now(), cust_status_index=cust_status_index)
            acct_details = Account_status.query.filter_by(ws_cust_id=cust_detail.ws_cust_id).all()
            for acct in acct_details:
                acct.ws_status="Deactive"
            db.session.add(cust_status)      # Making new status entry with delete status
            db.session.commit() 
            return jsonify({"status":True, "message":f"Customer with ssn {data.get('ws_ssn')} is deleted"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

############ API for customer reactivation ################

@app.route("/customerreactivate", methods=["POST"])
def customerreactivate():
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if Customer_status.query.filter_by(ws_ssn=data.get('ws_ssn')).first().ws_status=='Active':    # Checking customer status
                return jsonify({'status':False,'message':f"Customer with usn {data.get('ws_ssn')} is already active"})
            
            customer = Customer_status.query.filter_by(ws_ssn=data.get('ws_ssn')).all()
            for cust in customer:
                cust.ws_status = "Active"     # Changing status from Deactive to Active
            cust_status_index = Customer_status.query.count()+100000000
            cust = Customer.query.filter_by(ws_ssn=data.get('ws_ssn')).first()
            cust_status = Customer_status(ws_ssn=data.get('ws_ssn'), ws_cust_id=cust.ws_cust_id, ws_status="Active", ws_msg="Customer reactivation success",
            ws_lup=datetime.datetime.now(), cust_status_index=cust_status_index)
            db.session.add(cust_status)      # Making new status entry with reactivation status
            db.session.commit() 
            return jsonify({"status":True, "message":f"Customer with ssn {data.get('ws_ssn')} is reactivated"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

########### API for customer status ##############

@app.route("/customerstatus", methods=["POST"])
def customerstatus():
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            cust_status = Customer_status.query.all()
            result = customer_status_schema.dump(cust_status)    # Serializing database objects
            return jsonify({'status':True,'result':result})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

########## API for deactive customer status ##############

@app.route("/customersearchdistint", methods=["POST"])
def customersearchdistint():
    data = request.get_json()
    token = data.get('token')
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
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if Account.query.filter_by(ws_cust_id=data.get('ws_cust_id'),ws_acct_type=data.get('ws_acct_type')).first():   # Checking if for requested account is already exist with customer
                if data.get('ws_acct_type') =='s':
                    account_type = 'Saving'
                else:
                    account_type = 'Current'    
                return jsonify({'status':False,'message':f"Customer with id {data.get('ws_cust_id')} already has {account_type} account"})    # Returning the error message
            
            ac_id = Account.query.count()+100000000
            account = Account(ws_cust_id=data.get('ws_cust_id'),ws_acct_id=ac_id,ws_acct_type=data.get('ws_acct_type'),ws_acct_balance=float(data.get('ws_acct_balance')),
            ws_acct_crdate=datetime.datetime.now(), ws_acct_lasttrdate=datetime.datetime.now(),ws_acct_duration=0)   # Creating the Account
            db.session.add(account)
            account_status_id = Account_status.query.count()+100000000
            account_status = Account_status(ws_cust_id=data.get('ws_cust_id'),ws_acct_id=ac_id,ws_acct_type=data.get('ws_acct_type'),
            ws_status='Active',ws_cust_msg='Account created succesfully',ws_cust_lup=datetime.datetime.now(),acct_status_index=account_status_id)  # Making entry in Account status table
            db.session.add(account_status)
            db.session.commit()
            return jsonify({'status':True,'message':f"Account with id {ac_id} created successfully"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


########### API for account search ################

@app.route("/accountsearch", methods=["POST"])
def accountsearch():
    data = request.get_json()
    token = data.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if data.get('type')=='accountid':         # Checking search type
                if Account.query.filter_by(ws_acct_id=data.get('id')).first():   # Checking whether Account with given id exists or not
                    account = Account.query.filter_by(ws_acct_id=int(data.get('id'))).first() # Query to featch data
                    result = account_schema.dump(account)     # Serializing the database result
                    return jsonify({"status":True, "result":result})

                return jsonify({'status':False,'message':f"Account with id {data.get('id')} doesn't exist"})    
            
            if Account.query.filter_by(ws_cust_id=int(data.get('id'))).first():     # Checking whether Customer with given id exists or not
                account = Account.query.filter_by(ws_cust_id=int(data.get('id'))).all()
                result = accounts_schema.dump(account)
                return jsonify({"status":True, "result":result})

            return jsonify({'status':False,'message':f"Customer wih id {data.get('id')} doesn't exist"})

        return jsonify({'status':False,'message':'Not authorized'})   

    return jsonify({'status':False,'message':'Not authenticated'})

############ API for account delete ##################

@app.route("/accountdelete", methods=["POST"])
def accountdelete():
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if Account_status.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first().ws_status=='Deactive':      # Checking account status
                return jsonify({'status':False,'message':f"Account with id {data.get('ws_acct_id')} is already deactive"})

            account = Account_status.query.filter_by(ws_acct_id=data.get('ws_acct_id')).all()
            for acct in account:
                acct.ws_status = "Deactive"         # Changing status from Active to Deactive
            acct_status_id = Account_status.query.count()+100000000
            account = Account.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first()
            acct_status = Account_status(ws_acct_id=data.get('ws_acct_id'), ws_acct_type=account.ws_acct_type, ws_cust_id=account.ws_cust_id, ws_status="Deactive", ws_cust_msg="Account deleted successfully",
            ws_cust_lup=datetime.datetime.now(), acct_status_index=acct_status_id)
            db.session.add(acct_status)      # Making new status entry with delete status
            db.session.commit() 
            return jsonify({"status":True, "message":f"Account with id {data.get('ws_acct_id')} is deleted"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


############ API for account reactivation ###############

@app.route("/accountreactivate", methods=["POST"])
def accountreactivate():
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            if Account_status.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first().ws_status=='Active':    # Checking customer status
                return jsonify({'status':False,'message':f"Account with id {data.get('ws_acct_id')} is already active"})
            
            account = Account_status.query.filter_by(ws_acct_id=data.get('ws_acct_id')).all()
            for acct in account:
                acct.ws_status = "Active"     # Changing status from Deactive to Active
            acct_status_index = Account_status.query.count()+100000000
            acct = Account.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first()
            acct_status = Account_status(ws_acct_id=data.get('ws_acct_id'), ws_cust_id=acct.ws_cust_id, ws_status="Active", ws_cust_msg="Account reactivation success",
            ws_cust_lup=datetime.datetime.now(), acct_status_index=acct_status_index, ws_acct_type=acct.ws_acct_type)
            db.session.add(acct_status)      # Making new status entry with reactivation status
            db.session.commit() 
            return jsonify({"status":True, "message":f"Account with id {data.get('ws_acct_id')} is reactivated"})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

############ API for distinct account search ###############

@app.route("/accountsearchdistint", methods=["POST"])
def accountsearchdistint():
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            acct_status = Account_status.query.group_by(Account_status.ws_acct_id).distinct(Account_status.ws_acct_id).filter_by(ws_status="Deactive").all()
            if acct_status:
                result = account_status_schema.dump(acct_status)    # Serializing database objects
                return jsonify({'status':True,'result':result})

            return jsonify({'status':False, 'message':"There is no deactivate account currently"})    

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})

############# API for account status ###############

@app.route("/accountstatus", methods=["POST"])
def accountstatus():
    data = request.get_json()
    token = data.get('token')
    user = Userstore.query.filter_by(token=token).first()       # Checking for authentication using token
    if user:
        if user.user_role =='account executive':    # Checking authorization with user_role
            acct_status = Account_status.query.all()
            result = account_status_schema.dump(acct_status)    # Serializing database objects
            return jsonify({'status':True,'result':result})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


############ API for deposit amount ################

@app.route("/deposite", methods=["POST"])
def deposit():
    data = request.get_json()
    token = data.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if float(data.get('amount'))<=0:
                return jsonify({'status':False, 'message':'Amount must be grether than 0'})
            if Account_status.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first().ws_status=='Deactive':
                return jsonify({'status':False, 'message':f"Account with id {data.get('ws_acct_id')} is deactive please request for reactivation."})

            acct_details = Account.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first()
            acct_details.ws_acct_balance += float(data.get('amount'))
            acct_status_index = Account_status.query.count()+100000000
            transcation = Transcation(ws_cust_id=acct_details.ws_cust_id, ws_acct_type=acct_details.ws_acct_type, ws_amt=float(data.get('amount')),
            ws_trxn_date=datetime.datetime.now(), ws_src_typ='d', ws_tgt_typ=acct_details.ws_acct_type, trxn_id= tranx_id,description="Deposite")
            db.session.add(acct_status)      # Making new status entry with reactivation status
            db.session.add(transcation)
            db.session.commit() 
            return jsonify({'status':True, 'balance':acct_details.ws_acct_balance})

        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


############ API for withdraw ##############

@app.route("/withdraw", methods=["POST"])
def withdraw():
    data = request.get_json()
    token = data.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if float(data.get('amount'))<=0:
                return jsonify({'status':False, 'message':'Amount must be grether than 0'})
            if Account_status.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first().ws_status=='Deactive':
                return jsonify({'status':False, 'message':f"Account with id {data.get('ws_acct_id')} is deactive please request for reactivation."})

            account = Account.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first()
            if account.ws_acct_type=='s':
                if account.ws_acct_balance-float(data.get('amount'))>=0:
                    account.ws_acct_balance -= float(data.get('amount'))
                    tranx_id = Transcation.query.count()+100000000
                    transcation = Transcation(ws_cust_id=account.ws_cust_id, ws_acct_type=account.ws_acct_type, ws_amt=float(data.get('amount')),
                    ws_trxn_date=datetime.datetime.now(), ws_src_typ=account.ws_acct_type, ws_tgt_typ='w', trxn_id= tranx_id,description="Withdraw")
             
                    db.session.add(transcation)
                    db.session.commit()
                    return jsonify({'status':True, 'balance':account.ws_acct_balance})

                return jsonify({'status':False, 'message':"Insufficient balance"}) 

            if account.ws_acct_type=='c':
                if account.ws_acct_balance-float(data.get('amount'))>=-5000:
                    account.ws_acct_balance -= float(data.get('amount'))
                    tranx_id = Transcation.query.count()+100000000
                    transcation = Transcation(ws_cust_id=account.ws_cust_id, ws_acct_type=account.ws_acct_type, ws_amt=float(data.get('amount')),
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
    data = request.get_json()
    token = data.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if float(data.get('amount'))<=0:
                return jsonify({'status':False, 'message':'Amount must be grether than 0'})
            if Customer_status.query.filter_by(ws_cust_id=data.get('ws_cust_id')).first().ws_status=='Deactive':
                return jsonify({'status':False, 'message':f"Customer with id {data.get('ws_cust_id')} is deactive please request for reactivation."})

            if Account.query.filter_by(ws_cust_id=data.get('ws_cust_id'), ws_acct_type='s').first() and Account_status.query.filter_by(ws_cust_id=data.get('ws_cust_id'), ws_acct_type='s', ws_status='Active').first():    # Checking if customer has saving account
                if Account.query.filter_by(ws_cust_id=data.get('ws_cust_id'), ws_acct_type='c').first() and Account_status.query.filter_by(ws_cust_id=data.get('ws_cust_id'), ws_acct_type='c', ws_status='Active').first():    # Checking if customer has current account
                    src_type = data.get('ws_src_type')
                    trg_type = data.get('ws_trg_type')
                    if src_type =='s':                                                              # Checking if source account is saving
                        saving_account = Account.query.filter_by(ws_acct_type=src_type).first()
                        current_account = Account.query.filter_by(ws_acct_type=trg_type).first()
                        if saving_account.ws_acct_balance-float(data.get('amount'))>=0:             # Checking if transfering amount available in account
                            saving_account.ws_acct_balance -= float(data.get('amount'))             # Deducting amount from saving account
                            current_account.ws_acct_balance += float(data.get('amount'))            # Credicting amount in current account
                            tranx_id1 = Transcation.query.count()+100000000
                            transcation1 = Transcation(ws_cust_id=saving_account.ws_cust_id, ws_acct_type=src_type, ws_amt=float(data.get('amount')),
                            ws_trxn_date=datetime.datetime.now(), ws_src_typ=src_type, ws_tgt_typ=trg_type, trxn_id= tranx_id1,description="Transfer")
                            

                            tranx_id2 = Transcation.query.count()+100000000
                            transcation2 = Transcation(ws_cust_id=current_account.ws_cust_id, ws_acct_type=trg_type, ws_amt=float(data.get('amount')),
                            ws_trxn_date=datetime.datetime.now(), ws_src_typ=src_type, ws_tgt_typ=trg_type, trxn_id= tranx_id2,description="Transfer")
                            db.session.add(transcation1)        # Adding entry for saving account in Transaction table
                            db.session.add(transcation2)        # Adding entry for current account in Transaction table
                            db.session.commit()
                            return jsonify({'status':True, 'message':"Transfer completed"})

                        return jsonify({'status':False, 'message':"Insufficient balance"})

                    saving_account = Account.query.filter_by(ws_acct_type=trg_type).first()
                    current_account = Account.query.filter_by(ws_acct_type=src_type).first()
                    if current_account.ws_acct_balance-float(data.get('amount'))>=-5000:        # Checking if requested amount fell under overdraft amount or not
                        current_account.ws_acct_balance -= float(data.get('amount'))            # Deducting money from current account
                        saving_account.ws_acct_balance += float(data.get('amount'))             # Credicting money in saving account
                        tranx_id1 = Transcation.query.count()+100000000
                        transcation1 = Transcation(ws_cust_id=current_account.ws_cust_id, ws_acct_type=src_type, ws_amt=float(data.get('amount')),
                        ws_trxn_date=datetime.datetime.now(), ws_src_typ=src_type, ws_tgt_typ=trg_type, trxn_id= tranx_id1,description="Transfer")
                        

                        tranx_id2 = Transcation.query.count()+100000000
                        transcation2 = Transcation(ws_cust_id=current_account.ws_cust_id, ws_acct_type=trg_type, ws_amt=float(data.get('amount')),
                        ws_trxn_date=datetime.datetime.now(), ws_src_typ=src_type, ws_tgt_typ=trg_type, trxn_id= tranx_id2,description="Transfer")
                        db.session.add(transcation1)            # Adding entry for current account
                        db.session.add(transcation2)            # Adding entry for saving account
                        db.session.commit()
                        return jsonify({'status':True, 'message':"Transfer completed"})

                    return jsonify({'status':False, 'message':"Insufficient balance"})

                   
                return jsonify({'status':False, 'message':f"Customer with id {data.get('ws_cust_id')} doesn't have current account or account is deactivated"})
           
            return jsonify({'status':False, 'message':f"Customer with id {data.get('ws_cust_id')} doesn't have Saving account or account is deactivated"})
    
        

        
        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})


############ API for Transaction ###############

@app.route("/transactionhistory", methods=["POST"])    
def transactionhistory():
    data = request.get_json()
    token = data.get("token")
    user = Userstore.query.filter_by(token=token).first()    # Checking for authentication with token
    if user:
        if user.user_role =='cashier' or user.user_role =='teller':    # Checking authorization with user_role
            if Account_status.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first().ws_status=="Active":
                acct = Account.query.filter_by(ws_acct_id=data.get('ws_acct_id')).first()
                cust_id = acct.ws_cust_id
                acct_type = acct.ws_acct_type
                if data.get('type')=="no":
                    totaltransaction = int(data.get('number'))
                    trax_details = Transcation.query.filter_by(ws_cust_id=cust_id,ws_acct_type=acct_type).order_by(Transcation.trxn_id).limit(totaltransaction)
                    result = transcation_schema.dump(trax_details)
                    return jsonify({'status':True,'result':result})

                fromdate = data.get('from')
                todate = data.get('to')
                format_str = '%m/%d/%Y'
                fromdate_obj = datetime.datetime.strptime(fromdate, format_str)
                todate_obj = datetime.datetime.strptime(todate,format_str)
                trax_details = Transcation.query.filter_by(ws_cust_id=cust_id,ws_acct_type=acct_type).all()
                result = transcation_schema.dump(trax_details)
                final_result =[]
                for res in result:
                    if res['ws_trxn_date'] >=str(fromdate_obj.date()) and res['ws_trxn_date'] <=str(todate_obj.date()):
                        final_result.append(res)
                return jsonify({'status':True,'result':final_result})

            return jsonify({'status':False,'message':f"Account with id {data.get('ws_acct_id')} is deactivated, Please request for reactivation."})    


        return jsonify({'status':False,'message':'Not authorized'})
    
    return jsonify({'status':False,'message':'Not authenticated'})
import flask
from retailbank import db,ma

############### Creating database model ###########################

class Userstore(db.Model):
    login_id=db.Column(db.Integer, primary_key=True)
    password=db.Column(db.String(45),unique=False, nullable=False)
    time = db.Column(db.String(120), unique=False,nullable=False)
    token = db.Column(db.String(200),unique=True,nullable=True)
    user_role = db.Column(db.String(30),unique=False,nullable=False)


class Customer(db.Model):
	ws_ssn=db.Column(db.Integer,unique=True, nullable=False)
	ws_cust_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
	ws_name=db.Column(db.String(20),unique=False,nullable=False)
	ws_adrs=db.Column(db.String(200),unique=False,nullable=False)
	ws_age=db.Column(db.Integer,unique=False,nullable=False)
	accounts=db.relationship('Account',backref='accountof')
	c_status=db.relationship('Customer_status',backref='cstatus')
	a_status=db.relationship('Account_status',backref='astatus')
	trans=db.relationship('Transcation',backref='ctrans')

class Account(db.Model):
	ws_cust_id=db.Column(db.Integer,db.ForeignKey('customer.ws_cust_id'))
	ws_acct_id=db.Column(db.Integer, primary_key=True)
	ws_acct_type=db.Column(db.String(1),unique=False,nullable=False)
	ws_acct_balance=db.Column(db.Float,unique=False,nullable=False)
	ws_acct_crdate=db.Column(db.String(12),unique=False,nullable=False)
	ws_acct_lasttrdate=db.Column(db.String(12),unique=False,nullable=False)
	ws_acct_duration=db.Column(db.Integer,unique=False,nullable=False)
	ac_status=db.relationship('Account_status',backref='hasacstatus')

class Transcation(db.Model):
	ws_cust_id=db.Column(db.Integer,db.ForeignKey('customer.ws_cust_id'))
	ws_acct_type=db.Column(db.String(1),unique=False,nullable=False)
	ws_amt=db.Column(db.Float,unique=False,nullable=False)
	ws_trxn_date=db.Column(db.String(12),unique=False,nullable=False)
	ws_src_typ=db.Column(db.String(1),unique=False,nullable=False)
	ws_tgt_typ=db.Column(db.String(1),unique=False,nullable=False)
	trxn_id=db.Column(db.Integer,primary_key=True)

class Customer_status(db.Model):
	ws_ssn=ws_ssn=db.Column(db.Integer,unique=True, nullable=False)
	ws_cust_id=db.Column(db.Integer,db.ForeignKey('customer.ws_cust_id'))
	ws_status=db.Column(db.Integer,unique=False,nullable=False)
	ws_msg=db.Column(db.String(45),unique=False,nullable=False)
	ws_lup=db.Column(db.String(120),unique=False,nullable=False)
	cust_status_index=db.Column(db.Integer,primary_key=True)

class Account_status(db.Model):
	ws_cust_id=db.Column(db.Integer,db.ForeignKey('customer.ws_cust_id'))
	ws_acct_id=db.Column(db.Integer,db.ForeignKey('account.ws_acct_id'))
	ws_cust_typ=db.Column(db.String(1),unique=False,nullable=False)
	ws_cust_msg=db.Column(db.String(45),unique=False,nullable=False)
	ws_cust_lup=db.Column(db.String(120),unique=False,nullable=False)
	acct_status_index=db.Column(db.Integer,primary_key=True)    

class CustomerSchema(ma.Schema):
    class Meta:
        fields = ('ws_ssn','ws_cust_id','ws_name','ws_adrs','ws_age')

customer_schema = CustomerSchema()        


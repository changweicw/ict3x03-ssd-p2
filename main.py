from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_login import LoginManager, login_user,logout_user,login_required,current_user, UserMixin
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect,FlaskForm
from wtforms import StringField,FileField,DecimalField
from werkzeug.utils import secure_filename
import logging
from models import User, Product_listing
import os
import re
from appConfig import DefaultConfig
from dao.loginDAO.loginDAO import loginDAO
from dao.productDAO.productDAO import productDAO
from wtform import *
from google.cloud import storage
import uuid
from cloudstore_utils import cloudstore_utils as csutils
from mailing import *
from log_helper import *
import ipaddress
from io import BytesIO
from base64 import b64decode
from datetime import datetime,timedelta





app = Flask(__name__, template_folder="templates")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message="Please login first."

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.permanent_session_lifetime=timedelta(minutes=int(DefaultConfig.SESSION_TIMEOUT))

#========================================
#DATABASE
#========================================
# csrf = CSRFProtect(app)
app.config.from_object(DefaultConfig)
mysql = MySQL(app)
loginDAO = loginDAO(mysql)
productDAO = productDAO(mysql)

#========================================
#GOOGLE BUCKET INIT
#========================================
csu = csutils()
ALLOWED_EXTENSIONS = DefaultConfig.ALLOWED_EXTENSIONS

#========================================
#SERVER ENV
#========================================
server = "dev"
# server = "prod"
if server=="dev":
    ip = "127.0.0.1"
    port = "8080"

if server=="prod":
    ip="0.0.0.0"
    port="3389"
src = "http://"+ip+":"+port+"/"

#========================================
#LOGGER SETUPS
#========================================
logger = prepareLogger(__name__,'sys.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# ROOT LEVEL LOG
logging.basicConfig(filename=DefaultConfig.LOGGING_FOLDER+"/server.log",level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s")

#========================================
#FLASK FORMS
#========================================
class publishForm(FlaskForm):
    title = StringField("title")
    desc = StringField("desc")
    price = DecimalField("price")
    files = FileField("files")


@app.route('/test',methods=['GET', 'POST'])
def testing():
    csu.upload_to_bucket_b64List(request.get_json()['imageList'])
    # images = request.get_json()['imageList']
    # for image in images:
    #     decodedImage = b64decode(image)
    #     filename = 'uploads_temp/some_image.png' 
    #     with open(filename, 'wb') as f:
    #         f.write(decodedImage)
    return jsonify(success=True)

@app.route('/')
def landing():
    session['title'] = "Collaboratory Mall"
    # print(dbh.retrieve_all_products())
    print(str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(request.remote_addr)))))
    products = productDAO.retrieve_all_products()
    
    # sendLoginEmail("Raphael","raphaelisme@gmail.com")
    return render_template('landing.html',products=products)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account/my-account.html')


@app.route('/login', methods=['GET', 'POST'])
def login_landing():
    if current_user.is_authenticated:
        return render_template('/',products = productDAO.retrieve_all_products())

    login_form = LoginForm()
    ip_source = ipaddress.IPv4Address(request.remote_addr)
    registration_form = RegistrationForm()
    if login_form.validate_on_submit():
        login_result = loginDAO.check_login(login_form.username.data,
                                   login_form.password.data)
        if login_result:
            # Handle Redirect after login success
            print('TODO LOGIN')
            login_user(login_result)
            if loginDAO.is_new_login(login_result.iduser,int(ip_source)):
                sendLoginEmail(ip_source,login_result.email)

                # Redirect to landing page
            return redirect(url_for('landing'))
        else:
            flash('Your username or password is incorrect.', 'login')

    return render_template('account/login.html', form=login_form, reg_form=registration_form, src=src)


@app.route("/register", methods=['GET', 'POST'])
def registration():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    fname = registration_form.firstName.data
    lname = registration_form.lastName.data
    email = registration_form.email.data
    password = registration_form.password.data
    passwordConfirm = registration_form.confirmPassword.data
    successFlag = True
    tab = "reg"
    if registration_form.validate_on_submit():
        nameRegex = "(^[\w\s]{1,}[\w\s]{1,}$)"
        namePat = re.compile(nameRegex)
        emailRegex = "^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
        emailPat = re.compile(emailRegex)
        passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{8,}$"
        passwordPat = re.compile(passwordRegex)
        email_matched = re.search(emailPat, email)
        fname_matched=re.search(namePat,fname)
        lname_matched=re.search(namePat,lname)
        password_matched = re.search(
            passwordPat, password)
        if not email_matched:
            flash('Please enter a valid email', 'register')
            successFlag=False
            logger.warning("email failed regex")
        if password != passwordConfirm:
            flash('Please enter the same password for both fields', 'register')
            logger.warning("password don't match")
            successFlag=False
        else:
            if not password_matched:
                logger.warning("Password doesn't satisfy criteria")
                successFlag=False
                flash('Password must contain minimum 8 characters, with 1 uppercase, 1 lowercase, 1 digit & 1 special char', 'register')

        if loginDAO.email_exist(email):
            successFlag=False
            flash('Email Already Exist','register')
            logger.info("Register failed because "+email+" already exist")

        if not fname_matched or not lname_matched:
            successFlag=False
            logger.info("Firstname or lastname needs to be legitimate.")
            flash('First Name or last name might not be legitimate.','register')
        
        if successFlag:
            user = User(fname,lname,email,password)
            logger.info("Information sufficient to register.")
            loginDAO.signup(user)
            tab="log"
    else:
        logger.info("Not validate on submit")
    return render_template('account/login.html', form=login_form, reg_form=registration_form, src=src, tab=tab)


@app.route("/sell/publish_listing", methods=['POST'])
@login_required
def publish():
    # need to check file type and probably do a file scan
    # files = request.form.getlist("files")
    j = request.get_json()
    files = j['imageList']
    title = j["title"]
    desc = j["desc"]
    price = j["price"]
    if not isinstance(title,str) or not isinstance(desc,str) or not isinstance(price,str):
        return jsonify(success=False)
    urlList = []
    logger.info("Title:"+title+".Desc:"+desc+".Price:"+price)
    logger.info("Somebody is going to pubilish a listing with "+str(len(files))+" pictures")
    for f in files:
        if f.split(';')[0].split('/')[1] not in app.config['ALLOWED_EXTENSIONS'] or (len(f.split(',')[1]) - 814 )/1.37 / 1024 > 1024:
            return jsonify(success=False)
    # for f in files:
    #     csu.bucket_name=DefaultConfig.GOOGLE_BUCKET_ID
    #     public_url =  csu.upload_to_bucket(f)
    #     # tempSplit = str(public_url).split("/")
    #     urlList.append(public_url)
    fileList = []
    for f in files:
        fileList.append({'b64':f.split(',')[1],'file_ext':f.split(';')[0].split('/')[1]})
    urlList = csu.upload_to_bucket_b64List(fileList)

    # tempProd = Product_listing(title,desc,urlList,price,0) eventually replace the last 0 with iduser
    tempProd = Product_listing(title,desc,urlList,price,0)
    idprod = productDAO.publish_listing(tempProd)
    if idprod:
        logger.info("Some user has just published a product with id: "+str(idprod))
    else : 
        print("Some user publish failed")


    # dbh.upload_to_bucket(files[0].filename)
    return jsonify(success=True)


@app.route('/sell/dashboard')
@login_required
def sell_dashboard():
    dashboard={}
    
    dashboard["lifetime_revenue"] = str.format("${:,.2f}",67876.90)
    dashboard["wallet_amt"] = str.format("${:,.2f}",273.00)
    dashboard["star_rating_avg"] = 4.7
    return render_template('sell/sell_dashboard.html',dashboard = dashboard)

@app.route('/products/checkout')
@login_required
def checkout():
    td = {}
    td["Product1"]={"name":"Chia Seeds", "price":28, "quantity":3}
    td["Product2"]={"name":"Apple", "price":28.2, "quantity":4}

    total = 0.0
    for v in td.values():
        total +=(v["price"]*v["quantity"])

    return render_template('products/checkout.html',checkout_total = total,dict = td)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landing'))

@login_manager.user_loader
def load_user(iduser):
    return loginDAO.getUser(iduser)

@login_manager.unauthorized_handler
def getout():
    return redirect(url_for('login_landing'))


if __name__ == '__main__':
    app.secret_key=b'_5#y2L"4Q8z178s/\\n\xec]/'
    app.run(host=ip, port=port, debug=True)


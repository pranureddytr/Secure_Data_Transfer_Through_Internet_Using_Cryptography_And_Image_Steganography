# Importing all the libraries
from flask import Flask,render_template,request,redirect,url_for,session
from werkzeug.utils  import secure_filename
import os
from cryptosteganography import CryptoSteganography
import time
import random
import smtplib
# import glob, os
# import time

import smtplib

from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate

# Importing MYSQLDB module
import MySQLdb

#Uploaded files destination
UPLOAD_FOLDER =r'C://Users//Mrida//Documents//2023//image-steganography-master'
app = Flask(__name__)

# This configuration is for allowing all media types to be upload using flask-upload module
#all_files=UploadSet('media',ALL,default_dest=lambda x: 'media')


# Project app secret for session security
app.secret_key = "SECretK1Y"

# Assigning upload directory to app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Test route to see if application is running or not.
@app.route('/test')
def test():
    return "Tested and working properly."

# Main login route
@app.route('/')
def hello_world():
    return render_template('login.html')

# Route for rendering encryption web form
@app.route('/encrypt')
def encrypt():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('encrypt.html')


def send_mail(send_to, subject, files=None):
    gmail_user = 'steganograpgyteam.demo@gmail.com '
    gmail_password = 'password'

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    print('Debugging - login')

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)
    print('Debugging - testing mail notification')
    server.sendmail(gmail_user, send_to, msg.as_string())
    server.close()

# Route for actual encryption
@app.route('/convert',methods=['GET','POST'])
def convert():
    if request.method == 'POST':
        # check if post has file
        file = request.files['file']
        message = request.form['message']
        ps = request.form['password']
        filename = secure_filename(file.filename)
        num=random.randint(1,999)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        crypto_steganography = CryptoSteganography(ps)
        # Naming the stego file
        nm='stego'+str(num)+'.png'
        # Encrypting and hiding a message
        crypto_steganography.hide(os.path.join(app.config['UPLOAD_FOLDER'], filename),nm, message)
        msg='File encrypted successfully.'
        print('STEGO TEAM IN THE BUILDING')
        #send_mail('steganogrepgyteam.demo@gmail.com', 'Message Received- Stego', [os.path.join(app.config['UPLOAD_FOLDER'], filename)])
        return render_template('index.html',msg=msg)

# Route for rendering decryption web form
@app.route('/retrieve')
def retrieve():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('retrieve.html')

# Route for actual decryption
@app.route('/decrypt',methods=['GET','POST'])
def decrypt():
    if request.method == 'POST':
        # check if post has file
        file = request.files['file']
        pswd = request.form['password']
        filename = secure_filename(file.filename)
        filename_d='dec_'+filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename_d))
        time.sleep(10)
        # Decrypting file and retrieving message
        decipher = CryptoSteganography(pswd)
        secret = decipher.retrieve(filename_d)
        if secret == None:
            return render_template('incorrect.html')
        else:
            return render_template('message.html',secret=secret)

# Route for actual login from the database
@app.route('/login',methods=['GET','POST'])
def login():
    # DB Access
    global db2
    db2 = MySQLdb.connect("localhost", "root", "root", "stegnography")

    email = str(request.form.get('email'))
    password = str(request.form.get('password'))
    cursor2 = db2.cursor()
    sql_find="SELECT password from users where email="+"'"+email+"';"
    sql_find_str=str(sql_find)
    cursor2.execute(sql_find_str)
    db_pass=str(cursor2.fetchone()[0])
    db2.close()
    print(db_pass)
    #return "Your DB password is"+db_pass
    if db_pass == password:
        session['logged_in'] = True
        return render_template('index.html')
    return render_template('login.html',msg="Incorrect username/password")

# Route for rendering home page
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('index.html')

# Route to destroy session
@app.route('/logout')
def logout():
    if not session.get('logged_in'):
        return render_template('login.html',msg='You are not logged in.')
    else:
        session['logged_in'] = False
        return redirect('/')

# Route to render register page
@app.route('/reg')
def reg():
    return render_template('register.html')

# route to register from in database
@app.route('/register',methods=['GET','POST'])
def register():
    # DB Access
    global db
    db = MySQLdb.connect("localhost", "root", "root", "stegnography")
    if request.method=='POST':
        name = request.form['username']
        e_mail = request.form['email']
        passwd = request.form['password']
        f_name=str(name)
        f_e_mail=str(e_mail)
        f_passwd=str(passwd)
        cursor= db.cursor()
        sql = 'INSERT INTO users(user_name,email,password) VALUES("%s","%s","%s")' % (f_name, f_e_mail, f_passwd)
        cursor.execute(sql)
        db.commit()
        db.close()
        return render_template('login.html',msg="User created please login.")

# Server internal error handling
@app.errorhandler(500)
def internal_error(error):
    return render_template('incorrect.html')

# Start the application
if __name__ == '__main__':
    app.run(debug=True)

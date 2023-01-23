from flask import Flask,render_template,url_for,request,redirect,session,send_from_directory,flash
from requests import get 
from os.path import join
from flask_mysqldb import MySQL
from datetime import datetime
from py_mail import mail_sender
from email.message import EmailMessage
import smtplib
import os
from newsapi import NewsApiClient
#from config import api_key
#from os.path import join

app = Flask(__name__)
key="412bc2ffe7114659af692a9e27e4a030"


app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='lakshmi@2002'
app.config['MYSQL_DB']='NEWS'
mysql=MySQL(app)

app.secret_key=os.urandom(30)

from_mail="sepjune0306@gmail.com"
passcode="eihjpoubvtcpydj"



@app.route('/')
def home():
    return render_template('index.html')
@app.route('/signup',methods=["GET","POST"])
def signup():
    error=None
    success=None
    if request.method=="POST":
        fullname=request.form.get('fullname')
        password=request.form.get('password')
        confirmpassword=request.form.get('pass')
        email=request.form.get('email')
        cursor=mysql.connection.cursor()
        cursor.execute('select email from signup')
        emails=cursor.fetchall()
        mysql.connection.commit()
        cursor.close()
        if len(fullname)<4:
            error="YOUR NAME LOOKS INAVLID PLEASE ENTER VALID NAME"
        elif (email,) in emails:
            error="Sorry this Email-Id had used already"
        elif len(email)<6 :
            error="Your email should contain atleast 8 characters without accepting any special symbols only @"
        elif len(password)<6:
            error="Password should have atleast 8 characters and accepts any symbols,characters"
        elif password!=confirmpassword:
            error="Passwords not matched please enter same password"
        else:
            cursor=mysql.connection.cursor()
            #query="INSERT INTO signup(fullname,email,password,date) VALUES(%s,NULL,%s,NOW())"
            cursor.execute('insert into signup values(%s,%s,%s)',[fullname,email,password])
            mysql.connection.commit()
            cursor.close()
            
            success="YOUR ACCOUNT HAS BEEN CREATED SUCCESSFULLY"
            subject=f'YOUR ACCOUNT HAS BEEN CREATED SUCCESSFULLY{fullname}'
            body=f'\nYOUR ACCOUNT HAS BEEN CREATED SUCCESSFULLY{fullname} on account {email}\n\nThanks for being a member in our WORLD NEWS.\n\nHappy reading!'
            try:
                mail_sender(email,subject,body)
            except Exception as e:
                print(e)
            return redirect(url_for('login'))
    return render_template('si.html',error=error,msg=success)

'''@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=="POST":
        cursor=mysql.connection.cursor()
        fullname=request.form['fullname']
        cursor.execute('SELECT fullname from signup')
        data=cursor.fetchall()
        cursor.close()
        if (fullname,) in data:
            flash('FullName Id already exists')
            return render_template('si.html')
        email=request.form['email']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT email from signup')
        emails=cursor.fetchall()
        cursor.close()
        if (email,) in  emails:
            flash('Email already exists')
            return render_template('si.html')
        cursor=mysql.connection.cursor()
        password=request.form['password']
        cursor.execute('SELECT password from signup')
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO signup VALUES(%s,%s,%s)',
                       [fullname,email,password])
        mysql.connection.commit()
        flash('Details Registered Succesfully!')
        return redirect(url_for('login'))
    return render_template('si.html')'''

@app.route("/login",methods=["GET","POST"])
def login():
    error=None
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        if len(email)<6:
            error="YOUR EMAIL-ID IS INVALID PLEASE ENTER VALID MAIL ADDRESS"
        elif len(password)<6:
            error="PASSWORD IS EMPTY OR INVALID"
        else:
            cursor=mysql.connection.cursor()
            #query="select * from signup where email=%s and password=%s"
            cursor.execute('select * from signup where email=%s and password=%s',[email,password])
            rows=cursor.fetchall()
            countRows=cursor.rowcount
            mysql.connection.commit()
            cursor.close()
            if countRows<1:
                error="INVALID LOGIN DETAILS"
            else:
                session['email']=email
                subject=f'YOUR LOGIN PROCESS DONE SUCCESSFULLY'
                body=f'\nYOUR ACCOUNT HAS BEEN CREATED SUCCESSFULLY ON ACCOUNT {email}\n\nThanks for being a member in our WORLD NEWS.\n\nHappy reading!'
                try:
                    mail_sender(email,subject,body)
                except Exception as e:
                    print(e)
                return redirect(url_for('dashboard'))
                
    return render_template('login.html',error=error)


@app.route('/dashboard')
def dashboard():
    email=session.get("email")
    if email is None:
        return redirect(url_for('login'))
    return render_template('dashboard.html',email=email)

@app.route('/logout')
def logout():
    session.pop("email",None)
    return redirect(url_for('reopen'))


@app.route("/reopen")
def reopen():
    return render_template("reopen.html")


@app.route("/re")
def re():
    return render_template("re.html")

@app.route("/rating")
def re():
    return render_template("rating.html")

@app.route("/notes")
def re():
    return render_template("notes.html")




@app.route("/send",methods=["GET","POST"])
def send():
    error=None
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        if len(email)<6:
            error="YOUR EMAIL-ID IS INVALID PLEASE ENTER VALID MAIL ADDRESS"
        elif len(password)<6:
            error="PASSWORD IS EMPTY OR INVALID"
        else:
            cursor=mysql.connection.cursor()
            query="select * from signup where email=%s and password=%s"
            cursor.execute(query,(email,password))
            rows=cursor.fetchall()
            countRows=cursor.rowcount
            mysql.connection.commit()
            cursor.close()
            if countRows<1:
                error="INVALID LOGIN DETAILS"
            else:
                session['email']=email
                subject=f'We have sent all updated news to your account'
                body=f'\nView Updated News from Our WORLD NEWS \n\n Click Here --> https://codegnan.com\n\nThanks for being a member in our WORLD NEWS.\n\nHAVE A GREAT READING DAY!'
                try:
                    mail_sender(email,subject,body)
                except Exception as e:
                    print(e)
                return redirect(url_for('news'))
                
    return render_template('mail.html',error=error)
    

@app.route('/news')
def news():
    response1=get("https://newsapi.org/v2/top-headlines?country=in",params={'apikey':key,'category':'business'}).json()
    response2=get("https://newsapi.org/v2/top-headlines?country=in",params={'apikey':key,'category':'entertainment'}).json()
    response3=get("https://newsapi.org/v2/top-headlines?country=in",params={'apikey':key,'category':'general'}).json()
    response4=get("https://newsapi.org/v2/top-headlines?country=in",params={'apikey':key,'category':'health'}).json()
    response5=get("https://newsapi.org/v2/top-headlines?country=in",params={'apikey':key,'category':'science'}).json()
    response6=get("https://newsapi.org/v2/top-headlines?country=in",params={'apikey':key,'category':'sports'}).json()
    response7=get("https://newsapi.org/v2/top-headlines?country=in",params={'apikey':key,'category':'technology'}).json()
    return render_template('news.html',response1=response1,response2=response2,response3=response3,response4=response4,response5=response5,response6=response6,response7=response7)


@app.route('/search',methods=['post'])
def search():
    response=get("https://newsapi.org/v2/everything",params={'apikey':key,'q':request.form['searchBar']}).json()
    return render_template('search.html',response=response)


@app.route('/sources')
def sources():
    response=get('https://newsapi.org/v2/top-headlines/sources',params={'apikey':key}).json()
    return render_template('sources.html',name=response)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404                





if __name__ == '__main__':
    app.run(debug=True)



#,url_all

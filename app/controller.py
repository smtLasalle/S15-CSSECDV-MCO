from flask import render_template, request
from app import app
from app.model import *

@app.route('/')
def index():
    return render_template('budget-tracker.html')

@app.route('/submitRegister', methods=['POST'])
def submit():
    print("Bannaa")
    idnum = getID(1)
    print('check')
    username = request.form['username']
    email = request.form['email']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    phoneNumber = request.form['phoneNumber']
    password = request.form['password']
    confirmPass = request.form['confirmPassword']

    #insert CHECK FOR REDUNDANCY
    if newUserCheck(username,email,firstName,lastName,password,confirmPass,phoneNumber):
        insertNewUser(idnum,username,firstName,lastName, email, password, phoneNumber)
        return render_template('old-user.html')
    
    return render_template('/new-user.html')

@app.route('/old-user.html')
def login():
    return render_template('old-user.html')

@app.route('/new-user.html')
def signUp():
    return render_template('new-user.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/parent-dashboard.html')
def parentDashboard():
    return render_template('parent-dashboard.html')

@app.route('/parent-mail.html')
def parentMail():
    return render_template('parent-mail.html')

@app.route('/parent-profile.html')
def parentProfile():
    return render_template('parent-profile.html')

@app.route('/parent-settings.html')
def parentSettings():
    return render_template('parent-settings.html')

@app.route('/child-dashboard.html')
def childDashboard():
    return render_template('child-dashboard.html')

@app.route('/child-mail.html')
def childMail():
    return render_template('child-mail.html')

@app.route('/child-profile.html')
def childProfile():
    return render_template('child-profile.html')

@app.route('/child-settings.html')
def childSettings():
    return render_template('child-settings.html')

@app.errorhandler(404)
def notFound():
    return render_template('404.html')
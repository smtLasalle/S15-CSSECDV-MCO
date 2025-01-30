from flask import render_template, request
from app import app
from app.model import *
import time
import threading

registeredAccsAndTimes = []
timeout = []

def start_background_timer(username, rem):
    def timer_function():
        print('Countdown for ' + username + ' started')
        time.sleep(100)  # Wait for the specified duration
        print('Countdown for ' + username + ' finished')
        if not stop_event.is_set():
            timerEnd(username,rem)  # Call the callback function
    stop_event = threading.Event()

    timer_thread = threading.Thread(target=timer_function)
    timer_thread.start()

    return stop_event, timer_thread


def timerEnd(username,rem):
    global registeredAccsAndTimes
    global timeout
    registeredAccsAndTimes = [pair for pair in registeredAccsAndTimes if pair[0] != username]
    if rem:
        timeout.remove(username)

    

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
    isParent = request.form['accountType']

    #insert CHECK FOR REDUNDANCY
    if newUserCheck(username,email,firstName,lastName,password,confirmPass,phoneNumber):
        insertNewUser(idnum,username,firstName,lastName, email, password, phoneNumber, isParent)
        return render_template('old-user.html')
    
    return render_template('/new-user.html',email=email, firstName=firstName, lastName=lastName,
                           phoneNumber=phoneNumber,username=username)

@app.route('/old-user.html')
def loginPage():
    return render_template('old-user.html')

@app.route('/new-user.html')
def signUp():
    return render_template('new-user.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/login', methods=['POST'])
def login():
    global registeredAccsAndTimes
    [username,logger] = checkLogin(request.form['username'],request.form['password'])
    
    if logger==2 and username not in timeout:
        timerEnd(username,0)
        return render_template('/parent-dashboard.html')
    elif logger==1 and username not in timeout:
        timerEnd(username,0)
        return render_template('/child-dashboard.html')
    
    if not any(pair[0] == username for pair in registeredAccsAndTimes):
        registeredAccsAndTimes.append([username,0])

    for i,(user,count) in enumerate(registeredAccsAndTimes):
        if username==user:
            registeredAccsAndTimes[i][1] = count+1
            if registeredAccsAndTimes[i][1]>=5:
                print(username)
                timeout.append(username)
                stop_event, thread = start_background_timer(username,1)
                

    
    print(registeredAccsAndTimes)
    return render_template('/old-user.html')

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

@app.route('/logout')
def logout():
    return render_template('old-user.html')

@app.errorhandler(404)
def notFound():
    return render_template('404.html')

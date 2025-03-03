from flask import render_template, request, make_response, session, redirect, url_for
from app import app
from app.model import *
import time
import threading
import os
from datetime import datetime, timedelta

TIMEOUT_DURATION = timedelta(seconds=20) # Session timeout time

# Session settings
app.config['SECRET_KEY'] = os.urandom(12)  # Secure random key
app.config['PERMANENT_SESSION_LIFETIME'] = TIMEOUT_DURATION # Session timeout
app.config['SESSION_TYPE'] = 'filesystem'

registeredAccsAndTimes = []
timeout = []

def start_background_timer(username, rem):
    def timer_function():
        print('Countdown for ' + username + ' started')
        time.sleep(20)  # Wait for the specified duration
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

@app.before_request
def check_session_timeout():
    # Check if logged in
    if 'username' in session:
        # Get last activity time
        last_activity_str = session.get('last_activity')
        if last_activity_str:
            last_activity = datetime.strptime(last_activity_str, '%Y-%m-%d %H:%M:%S')
            # Check if session has expired
            if datetime.now() - last_activity > TIMEOUT_DURATION:
                session.clear()
                return render_template('old-user.html', error_message = "Invalid username or password!")
                return render_template('old-user.html', error_message = "Session Timeout, Please Log in again")
            else:
                # Update activity time
                session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            # If there's no last activity time, set one
            session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    name = session.get('username')
    if name:  # If logged in, redirect to dashboard
        return redirect('/dashboard.html')
    
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
    flag = newUserCheck(username,email,firstName,lastName,password,confirmPass,phoneNumber)
    
    if flag == 1:
        insertNewUser(idnum, username, firstName, lastName, email, password, phoneNumber)
        return render_template('old-user.html', username=username)
    if flag == 0:
        error_message = "Passwords don't match!"
    if flag == -1:
        error_message = "Username in use!"
    if flag == -2:
        error_message = "Email in use!"
    if flag == -3:
        error_message = "Phone number in use!"
    
    return render_template('/new-user.html',email=email, firstName=firstName, lastName=lastName,
                           phoneNumber=phoneNumber,username=username, error_message = error_message)

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
    [username,isAdmin] = checkLogin(request.form['username'],request.form['password'])
    print(isAdmin)
    if username not in timeout: # LOGIN
        session.permanent = True  # Permanent session (session exist after browser closing)
        session['username'] = username
        session['isAdmin'] = str(isAdmin)
        session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timerEnd(username, 0)
        return redirect('/dashboard.html')

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
    return render_template('old-user.html', username=username, error_message = "Invalid username or password!")

@app.route('/saveProfile', methods=['POST'])
def saveProfile():
    picture = request.files['file']
    bytePicture = picture.read()
    username = session.get('username')
    if saveToDB(bytePicture, username): # USER PROFPIC CHANGES
        return render_template('dashboard.html')
    return render_template('profile.html')

@app.route('/dashboard.html')
def dashboard():
    isAdmin = session.get('isAdmin')
    if not session.get('username'):  # Check if logged in
        return redirect('/old-user.html')
    
    if isAdmin == '0':
        return render_template('dashboard.html')
    elif isAdmin == '1':
        return redirect('chief.html')

@app.route('/profile.html')
def profile():
    name = session.get('username')
    isAdmin = session.get('isAdmin')
    
    if not name:  # If not logged in, redirect to login page
        return redirect('/old-user.html')
    
    if isAdmin=='0':
        role = "User"
    elif isAdmin == '1':
        role = "Admin"
        
    [user,email,data] = retrieveData(name)
    if data==0:
        return render_template('profile.html',username=user,email=email,image=data, defaultHidden="", profHidden="hidden", role = role)
    return render_template('profile.html',username=user,email=email,image=data, defaultHidden="hidden", profHidden="", role = role)

@app.route('/settings.html')
def settings():
    name = session.get('username')
    
    if not name:  # If not logged in, redirect to login page
        return redirect('/old-user.html')
    
    return render_template('settings.html')

'''
@app.route('/child-profile.html')
def childProfile():
    name=request.cookies.get('un')
    [user,email, data] = retrieveData(name)
    if data==0:
        return render_template('child-profile.html',username=user,email=email,image=data, defaultHidden="", profHidden="hidden")
    return render_template('child-profile.html',username=user,email=email, image=data, defaultHidden="hidden", profHidden="")
'''

@app.route('/logout')
def logout():
    session.clear()
    return make_response(render_template('/budget-tracker.html'))

@app.route('/chief.html')
def admin():
    name = session.get('username')

    if not name:  # If not logged in, redirect to login page
        return redirect('/old-user.html')
    [user,email,data] = retrieveData(name)
    if data==0:
        return render_template('chief.html', image=data, defaultHidden="", profHidden="hidden")
    return render_template('chief.html', image=data, defaultHidden="hidden", profHidden="")

@app.errorhandler(404)
def notFound(e):
    return render_template('404.html')
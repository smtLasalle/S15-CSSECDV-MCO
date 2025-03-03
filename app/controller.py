from flask import render_template, request, make_response, session, redirect, url_for
from app import app
from app.model import *
import time
import threading
import os
from datetime import datetime, timedelta

TIMEOUT_DURATION = timedelta(seconds=3) # Session timeout time
MAX_LOGIN_ATTEMPTS = 5  # Maximum failed login attempts before timeout
LOCKOUT_DURATION = 20  # Lockout duration in seconds

# Session settings
app.config['SECRET_KEY'] = os.urandom(12)  # Secure random key
app.config['PERMANENT_SESSION_LIFETIME'] = TIMEOUT_DURATION # Session timeout
app.config['SESSION_TYPE'] = 'filesystem'

# Track IP addresses instead of usernames
ip_attempt_tracker = []  # List of [ip_address, attempt_count] pairs
ip_timeout_list = []     # List of IP addresses that are currently timed out

def start_background_timer(ip_address, rem):
    def timer_function():
        print(f'Countdown for IP {ip_address} started')
        time.sleep(LOCKOUT_DURATION)  # Wait for the specified duration
        print(f'Countdown for IP {ip_address} finished')
        if not stop_event.is_set():
            timer_end(ip_address, rem)  # Call the callback function
    stop_event = threading.Event()

    timer_thread = threading.Thread(target=timer_function)
    timer_thread.start()

    return stop_event, timer_thread

def timer_end(ip_address, rem):
    global ip_attempt_tracker
    global ip_timeout_list
    ip_attempt_tracker = [pair for pair in ip_attempt_tracker if pair[0] != ip_address]
    if rem:
        ip_timeout_list.remove(ip_address)

@app.before_request
def check_session_timeout():
    # Check if logged in
    if 'username' in session:
        # Get last activity time
        last_activity_str = session.get('last_activity')
        if last_activity_str:
            last_activity = datetime.strptime(last_activity_str, '%Y-%m-%d %H:%M:%S')
            # Check if session has expired
            print(f"\n{session.items}\n")
            print(f"endpoint:   {request.endpoint}")
            print(f"lastact:    {last_activity}")
            print(f"datenow:    {datetime.now()}")
            print(f"diff:       {datetime.now() - last_activity}")
            if (datetime.now() - last_activity > TIMEOUT_DURATION):
                print("session timeout detected??")
                x = 0
                #while(x < 1000000000):
                #    x+=1
                #session.clear()
                print("session timeout detected!")
                return render_template('about.html', error_message = "Session Timeout, Please Log in again")
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
    global ip_attempt_tracker
    global ip_timeout_list
    
    ip_address = request.remote_addr # Client IP address
    
    if ip_address in ip_timeout_list: # Check if IP is already in timeout
        error_message = f"Too many failed login attempts. Please try again in {LOCKOUT_DURATION} seconds"
        #error_message = "Too many failed login attempts. Please try again later."
        return render_template('old-user.html', error_message=error_message)
    
    [username,isAdmin] = checkLogin(request.form['username'],request.form['password'])
    if isAdmin != -1: # LOGIN
        session.permanent = True  # Permanent session (session exist after browser closing)
        session['username'] = username
        session['isAdmin'] = str(isAdmin)
        session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Clear attempts for IP
        ip_attempt_tracker = [pair for pair in ip_attempt_tracker if pair[0] != ip_address]
        return render_template('/dashboard.html')

    else:  # Failed login
        # Check if IP is already being tracked
        if not any(pair[0] == ip_address for pair in ip_attempt_tracker):
            ip_attempt_tracker.append([ip_address, 1])
        else:
            for i, (ip, count) in enumerate(ip_attempt_tracker):
                if ip_address == ip:
                    ip_attempt_tracker[i][1] = count + 1 # Inc attempt
                    
                    # If max attempts reached
                    if ip_attempt_tracker[i][1] >= MAX_LOGIN_ATTEMPTS:
                        print(f"IP {ip_address} has been timed out")
                        ip_timeout_list.append(ip_address)
                        stop_event, thread = start_background_timer(ip_address, 1)
        
        print(ip_attempt_tracker)           
    
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
        return render_template('/old-user.html', error_message = "dash")
    
    if isAdmin == '0':
        return render_template('dashboard.html')
    elif isAdmin == '1':
        return redirect('chief.html')

@app.route('/profile.html')
def profile():
    name = session.get('username')
    isAdmin = session.get('isAdmin')
    
    if not name:  # If not logged in, redirect to login page
        return render_template('/old-user.html', error_message = "prof")
    
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
        return render_template('/old-user.html', error_message = "settings")
    
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
        return render_template('/old-user.html', error_message = "admin")
    [user,email,data] = retrieveData(name)
    if data==0:
        return render_template('chief.html', image=data, defaultHidden="", profHidden="hidden")
    return render_template('chief.html', image=data, defaultHidden="hidden", profHidden="")

@app.errorhandler(404)
def notFound(e):
    return render_template('404.html')
from flask import render_template, request,make_response
from app import app
from app.model import *
import time
import threading

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
    if isAdmin == 0 and username not in timeout: # USER LOGIN
        response = make_response(render_template('/dashboard.html'))
        response.set_cookie('un',str(username))
        response.set_cookie('iA',str(isAdmin))
        timerEnd(username,0)
        return response
    elif isAdmin >= 1 and username not in timeout: # ADMIN LOGIN
        response = make_response(render_template('/chief.html'))
        response.set_cookie('un',str(username))
        response.set_cookie('iA',str(isAdmin))
        timerEnd(username,0)
        return response

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
    #filename = secure_filename(picture.filename)
    filename = picture.filename
    bytePicture = picture.read()
    username = request.cookies.get('un')
    isAdmin = request.cookies.get('iA')
    if isAdmin=='0':
        if saveToDB(bytePicture, username): # USER PROFPIC CHANGES
            return render_template('dashboard.html')
        return render_template('profile.html')
    else:
        if saveToDB(bytePicture, username): # ADMIN PROFPIC CHANGES
            return render_template('chief.html')
        return render_template('profile.html')

@app.route('/dashboard.html')
def dashboard():
    isAdmin = request.cookies.get('iA')
    if isAdmin=='0':
        return render_template('dashboard.html')
    else:
        return render_template('chief.html')

@app.route('/profile.html')
def profile():
    name=request.cookies.get('un')
    isAdmin = request.cookies.get('iA')
    if isAdmin=='0':
        role = "User"
    else:
        role = "Admin"
        
    [user,email,data] = retrieveData(name)
    if data==0:
        return render_template('profile.html',username=user,email=email,image=data, defaultHidden="", profHidden="hidden", role = role)
    return render_template('profile.html',username=user,email=email,image=data, defaultHidden="hidden", profHidden="", role = role)

@app.route('/settings.html')
def settings():
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
    response = make_response(render_template('/budget-tracker.html'))
    for cookie in request.cookies:
        response.delete_cookie(cookie)
    return response

@app.route('/chief.html')
def admin(): # photo no work, why???
    name=request.cookies.get('un')
    [user,email,data] = retrieveData(name)
    if data==0:
        return render_template('chief.html', image=data, defaultHidden="", profHidden="hidden")
    return render_template('chief.html', image=data, defaultHidden="hidden", profHidden="")

@app.errorhandler(404)
def notFound(e):
    return render_template('404.html')
from flask import render_template, request, make_response, session, redirect, url_for
from app import app
from app.model import *
import time
import threading
import os
import traceback
from datetime import datetime, timedelta

TIMEOUT_DURATION = timedelta(seconds=300) # Session timeout time
MAX_LOGIN_ATTEMPTS = 5  # Maximum failed login attempts before timeout
LOCKOUT_DURATION = 20  # Lockout duration in seconds
DEBUG_FLAG = False # For detailed errors. False in production

# Session settings
app.config['SECRET_KEY'] = os.urandom(12)  # Secure random key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15) # Session timeout failsafe
app.config['SESSION_TYPE'] = 'filesystem'

# Track IP addresses instead of usernames
ip_attempt_tracker = {}  # Dictionary of [ip_address, attempt_count] pairs
ip_timeout_list = []     # List of IP addresses that are currently timed out

print(f"New server session started at {datetime.now()}")

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
    if ip_address in ip_attempt_tracker:
        del ip_attempt_tracker[ip_address]
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
            if (datetime.now() - last_activity > TIMEOUT_DURATION):
                print(f"[{datetime.now()}] Session with username [{session.get('username')}] timed out")
                session.clear()
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
    idnum = getID(1)
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
        print(f"[{datetime.now()}] User [{session.get('username')}] was registered")
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
        #error_message = f"Too many failed login attempts. Please try again in {LOCKOUT_DURATION} seconds"
        error_message = "Too many failed login attempts. Please try again later."
        print(f"[{datetime.now()}] IP address [{ip_address}] locked out for too many login attempts")
        return render_template('old-user.html', error_message=error_message)
    
    [username,isAdmin] = checkLogin(request.form['username'],request.form['password'])
    if isAdmin != -1: # LOGIN
        session.permanent = True  # Permanent session (session exist after browser closing)
        session['username'] = username
        session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{datetime.now()}] IP address [{ip_address}] logged in with username [{username}]")
        
        # Clear attempts for IP
        if ip_address in ip_attempt_tracker:
            del ip_attempt_tracker[ip_address]
        return redirect('/dashboard.html')

    else:  # Failed login
        # Check if IP is already being tracked
        print(f"[{datetime.now()}] IP address [{ip_address}] attempting to login with username [{username}].", end=" ")
        if ip_address not in ip_attempt_tracker:
            ip_attempt_tracker[ip_address] = 1
            print(f"Attempts = {ip_attempt_tracker[ip_address]}")
        else:
            ip_attempt_tracker[ip_address] += 1  # Inc attempt
            print(f"Attempts = {ip_attempt_tracker[ip_address]}")
            # If max attempts reached
            if ip_attempt_tracker[ip_address] >= MAX_LOGIN_ATTEMPTS:
                print(f"IP {ip_address} has been timed out")
                ip_timeout_list.append(ip_address)
                stop_event, thread = start_background_timer(ip_address, 1)         
    
    return render_template('old-user.html', username=username, error_message = "Invalid username or password!")

@app.route('/saveProfile', methods=['POST'])
def saveProfile():
    picture = request.files['file']
    bytePicture = picture.read()
    username = session.get('username')
    if saveToDB(bytePicture, username): # USER PROFPIC CHANGES
        print(f"[{datetime.now()}] User [{username}] updated profile picture")
        return render_template('dashboard.html')
    return render_template('profile.html')

@app.route('/dashboard.html')
def dashboard():
    name = session.get('username')
    if not name:  # Check if logged in
        return redirect('/old-user.html')
    
    user = retrieveData(name)
    user_id = user['user_id']
    expenses = get_expenses(user_id)
    goals = get_goals(user_id)
    
    return render_template('dashboard.html', **user, expenses=expenses, goals=goals)


@app.route('/profile.html')
def profile():
    name = session.get('username')
    if not name:  # If not logged in, redirect to login page
        return redirect('/old-user.html')
    
    user = retrieveData(name)

    if not user['image']:
        return render_template('profile.html', **user, defaultHidden="", profHidden="hidden")
    return render_template('profile.html',**user, defaultHidden="hidden", profHidden="")

@app.route('/settings.html')
def settings():
    name = session.get('username')
    if not name:  # If not logged in, redirect to login page
        return redirect('/old-user.html')
    
    user = retrieveData(name)
    
    return render_template('settings.html', isAdmin=user['isAdmin'])

@app.route('/logout')
def logout():
    username = session.get('username')
    print(f"[{datetime.now()}] User [{username}] logged out")
    session.clear()
    return make_response(render_template('/budget-tracker.html'))

@app.route('/chief.html')
def admin():
    name = session.get('username')

    if not name:  # If not logged in, redirect to login page
        return redirect('/old-user.html')
    
    user = retrieveData(name)
    if not user['isAdmin']:
        return redirect('/dashboard.html')

    if not user['image']:
        return render_template('chief.html', image=user['image'], defaultHidden="", profHidden="hidden")
    return render_template('chief.html', image=user['image'], defaultHidden="hidden", profHidden="")

@app.route('/set_balance', methods=['POST'])
def set_balance():
    name = session.get('username')
    if not name:  # Check if logged in
        return redirect('/old-user.html')
    
    amount = request.form['amount']
    update_balance(name, amount)
    print(f"[{datetime.now()}] User [{name}] updated balance to {amount}")
    
    return redirect('/dashboard.html')

@app.route('/add_expense', methods=['POST'])
def add_expense():
    name = session.get('username')
    if not name:  # Check if logged in
        return redirect('/old-user.html')
    
    user = retrieveData(name)
    title = request.form['title']
    price = request.form['price']
    expense_date = request.form.get('expense_date') or datetime.today().strftime("%Y-%m-%d")
    isIncome = int(request.form.get('isIncome', 0))  
    
    if not title:
        title = 'Income' if isIncome else 'Expense'
    
    user_id = user['user_id']
    add_transaction(user_id, title, price, expense_date, isIncome)
    
    # Update balance if it's an expense
    if int(isIncome) == 0:
        user = retrieveData(name)
        new_balance = user['net_worth'] - int(price)
        update_balance(name, new_balance)
    else:
        user = retrieveData(name)
        new_balance = user['net_worth'] + int(price)
        update_balance(name, new_balance)
    
    print(f"[{datetime.now()}] User [{name}] added {'income' if int(isIncome) else 'expense'}: {title} - {price}")
    
    return redirect('/dashboard.html')

@app.route('/add_goal', methods=['POST'])
def add_goal():
    name = session.get('username')
    if not name:  # Check if logged in
        return redirect('/old-user.html')
    
    user = retrieveData(name)
    goal_name = request.form['goal_name'] or 'Goal'
    price = request.form['price']
    
    user_id = user['user_id']
    add_user_goal(user_id, goal_name, price)
    
    print(f"[{datetime.now()}] User [{name}] added goal: {goal_name} - {price}")
    
    return redirect('/dashboard.html')

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    name = session.get('username')
    if not name:  # Check if logged in
        return redirect('/old-user.html')
    
    # Get the expense details before deleting
    user = retrieveData(name)
    expense = get_expense_by_id(expense_id)
    if expense and expense[0] == user['user_id']:  # Verify the expense belongs to the user
        # Update balance if deleting an expense
        user = retrieveData(name)
        if expense[4] == 0:  # It was an expense
            new_balance = user['net_worth'] + expense[2]
        else:  # It was income
            new_balance = user['net_worth'] - expense[2]
        
        update_balance(name, new_balance)
        delete_expense_by_id(expense_id)
        print(f"[{datetime.now()}] User [{name}] deleted {'income' if expense[4] else 'expense'}: {expense[1]}")
    
    return redirect('/dashboard.html')

@app.route('/delete_goal/<int:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    name = session.get('username')
    if not name:  # Check if logged in
        return redirect('/old-user.html')
    
    # Verify the goal belongs to the user
    user = retrieveData(name)
    goal = get_goal_by_id(goal_id)
    if goal and goal[0] == user['user_id']:
        delete_goal_by_id(goal_id)
        print(f"[{datetime.now()}] User [{name}] deleted goal: {goal[1]}")
    
    return redirect('/dashboard.html')

@app.errorhandler(Exception)
def notFound(e):
    name = session.get('username')
    user = retrieveData(name)
    
    code = 500
    errstr = "We can't find the page you're looking for."

    if (user and user['isAdmin'] == 1) or DEBUG_FLAG:
        stack_trace = traceback.format_exc()
        if hasattr(e, 'code'):
            code = e.code
        errstr = f"<b>Error:</b> {str(e)}<br><br><b>Stack Trace:</b><br><pre>{stack_trace}</pre>"

    return render_template('error.html', e_code=code, error=errstr)
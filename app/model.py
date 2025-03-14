from app import db
import bcrypt
import base64
import re
import io

def getID(inc):
    cursor = db.cursor()
    #print(cursor)
    try:
        cursor.execute("SELECT MAX(user_id) FROM web_user")
        #print(cursor)
    except Exception as e:
        print("error somewhere", e)
    #print('Getting ID')
    result = cursor.fetchone()
    if not result[0]:
        return 1
    #print(result[0])
    if inc:
        return result[0]+1
    return result[0]

def newUserCheck(username,email,firstName,lastName,password,confirmPass,phoneNumber):
    flag = 0 # If passwords don't match
    if (password == confirmPass and bool(username) and checkEmail(email) 
        and bool(firstName) and bool(lastName) and checkPhone(phoneNumber)):
        flag = 1  # If new user

    cursor = db.cursor(buffered=True)
    query = "SELECT username, email, phone_number FROM web_user WHERE username = %s OR email = %s OR phone_number = %s"
    cursor.execute(query, (username, email, phoneNumber))
    result = cursor.fetchone()

    if result:
        if result[0] == username:
            return -1  # Username exists
        elif result[1] == email:
            return -2  # Email exists
        elif result[2] == phoneNumber:
            return -3  # Phone number exists
    
    return flag

def insertNewUser(userid, username, firstName, lastName, email, password, phoneNumber):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=15,prefix=b'2b')
    hashed = bcrypt.kdf(
        password=bytes,
        salt=salt,
        desired_key_bytes=32,
        rounds=178
    )
    cursor = db.cursor()
    profImg = None
    isAdmin = 0
    #print("pass: " + str(hashed))
    query = "INSERT INTO web_user (user_id, username, isAdmin, prof_img, first_name, last_name, email, phone_number, password, salt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (userid, username, isAdmin, profImg, firstName, lastName, email, phoneNumber, str(hashed), salt))
    db.commit()

def checkPhone(phone):
    valid = re.match(r'\+[6][3][\d]{10}$',phone)
    if valid:
        return 1
    return 0

def checkEmail(email):
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
    if valid:
        return 1
    return 0

def checkLogin(username, password):
    if password == "":
        return [username,-1] # invalid login
    
    cursor = db.cursor()
    query = "SELECT * FROM web_user WHERE username = %s"
    cursor.execute(query,[username])
    result = cursor.fetchone()
    if result:
        hashed = bcrypt.kdf(
            password=password.encode('utf-8'),
            salt=result[9].encode('utf-8'),
            desired_key_bytes=32,
            rounds=178
        )
        #print(result[8].encode('utf-8'))
        #print(password.encode('utf-8'))
        if str(hashed)==str(result[8]):
            return [username,result[2]]
        
    return [username,-1] # invalid login

def retrieveData(username):
    if username is None:
        return None
    
    #print("retrieve: "+ username)
    cursor = db.cursor()
    query = "SELECT * FROM web_user WHERE username = %s"
    cursor.execute(query,[username])
    result = cursor.fetchone()
    
    if result is None:
        return None
    
    # Convert image data to base64 if available
    image = base64.b64encode(result[3]).decode('utf-8') if result[3] else None
    
    return {
        "user_id": result[0],
        "username": result[1],
        "isAdmin": result[2],
        "first_name": result[4],
        "last_name": result[5],
        "email": result[6],
        "phone_number": result[7],
        "birth_date": result[10],
        "account_date": result[11],
        "net_worth": result[12],
        "image": image
    }

def saveToDB(data, username):
    cursor = db.cursor()
    
    query = "SELECT user_id FROM web_user WHERE username=%s"
    cursor.execute(query,[username])
    result = cursor.fetchone()
    
    if not result:
        print("User not found. You shouldn't be here")
        return False
    
    user_id = result[0]
    valid = False
    
    signatures = {
                b'\xff\xd8\xff': 'JPEG',
                b'\x89PNG\r\n\x1a\n': 'PNG',
            }
            
    for sig, format_name in signatures.items():
        if data.startswith(sig):
            valid = True
    
    if not valid:       
        return False
    
    try:
        if result:
            query = "UPDATE web_user SET prof_img = %s WHERE user_id = %s"
            cursor.execute(query, [data, user_id])
        else:
            '''
            query = "SELECT max(img_id) FROM profile_img"
            cursor.execute(query)
            result = cursor.fetchone()
            if result[0]:
                max = result[0]+1
            else:
                max = 1

            query = "INSERT INTO profile_img (img_id, filename, data, user_id) VALUES (%s,%s,%s,%s)"
            cursor.execute(query,[max,data,user_id])
            '''
            
        db.commit()
    except Exception as e:
        print("didnt work sad:", e)
        return False

    return True

def update_balance(username, amount):
    cursor = db.cursor()
    query = "UPDATE web_user SET net_worth = %s WHERE username = %s"
    cursor.execute(query, (amount, username))
    db.commit()
    
def add_transaction(user_id, title, price, expense_date, isIncome):
    cursor = db.cursor()
    query = "INSERT INTO expense_list (user_id, title, price, expense_date, isIncome) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (user_id, title, price, expense_date, isIncome))
    db.commit()
    return cursor.lastrowid  # Returns the auto-incr expense_id

def get_expenses(user_id):
    cursor = db.cursor()
    query = "SELECT expense_id, title, price, expense_date, isIncome FROM expense_list WHERE user_id = %s ORDER BY expense_date DESC"
    cursor.execute(query, [user_id])
    return cursor.fetchall()

def add_user_goal(user_id, goal_name, price):
    cursor = db.cursor()
    query = "INSERT INTO goal_list (user_id, goal_name, price) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, goal_name, price))
    db.commit()
    return cursor.lastrowid  # Returns the auto-incr goal_id

def get_goals(user_id):
    cursor = db.cursor()
    query = "SELECT goal_id, goal_name, price FROM goal_list WHERE user_id = %s"
    cursor.execute(query, [user_id])
    return cursor.fetchall()

def get_expense_by_id(expense_id):
    cursor = db.cursor()
    query = "SELECT user_id, title, price, expense_date, isIncome FROM expense_list WHERE expense_id = %s"
    cursor.execute(query, [expense_id])
    return cursor.fetchone()

def delete_expense_by_id(expense_id):
    cursor = db.cursor()
    query = "DELETE FROM expense_list WHERE expense_id = %s"
    cursor.execute(query, [expense_id])
    db.commit()

def get_goal_by_id(goal_id):
    cursor = db.cursor()
    query = "SELECT user_id, goal_name, price FROM goal_list WHERE goal_id = %s"
    cursor.execute(query, [goal_id])
    return cursor.fetchone()

def delete_goal_by_id(goal_id):
    cursor = db.cursor()
    query = "DELETE FROM goal_list WHERE goal_id = %s"
    cursor.execute(query, [goal_id])
    db.commit()
    
def get_all_users(current_admin_username=None):
    cursor = db.cursor()
    if current_admin_username:
        query = """
        SELECT username, email, first_name, last_name, isAdmin, phone_number, birth_date, account_date, user_id 
        FROM web_user
        WHERE username != %s
        """
        cursor.execute(query, [current_admin_username])
    else:
        query = """
        SELECT username, email, first_name, last_name, isAdmin, phone_number, birth_date, account_date, user_id 
        FROM web_user
        """
        cursor.execute(query)
    result = cursor.fetchall()
    return result

def get_users_count():
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM web_user WHERE isAdmin = 0"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def get_admins_count():
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM web_user WHERE isAdmin = 1"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def get_transactions_count():
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM expense_list"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def update_user(user_id, first_name, last_name, phone_number, birth_date, isAdmin):
    cursor = db.cursor()
    query = """
    UPDATE web_user 
    SET first_name = %s, last_name = %s, phone_number = %s, birth_date = %s, isAdmin = %s
    WHERE user_id = %s
    """
    cursor.execute(query, (first_name, last_name, phone_number, birth_date, isAdmin, user_id))
    db.commit()
    
def reset_user_password(user_id, new_password):
    if not new_password:
        return False

    bytes = new_password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=15, prefix=b'2b')
    hashed = bcrypt.kdf(
        password=bytes,
        salt=salt,
        desired_key_bytes=32,
        rounds=178
    )
    
    cursor = db.cursor()
    query = "UPDATE web_user SET password = %s, salt = %s WHERE user_id = %s"
    cursor.execute(query, (str(hashed), salt, user_id))
    db.commit()
    return True
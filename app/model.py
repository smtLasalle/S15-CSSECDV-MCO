from app import db
import bcrypt
import base64
import re


def getID(inc):
    cursor = db.cursor()
    print(cursor)
    try:
        cursor.execute("SELECT MAX(user_id) FROM web_user")
        print(cursor)
    except Exception as e:
        print("error somewhere", e)
    print('Getting ID')
    result = cursor.fetchone()
    if not result[0]:
        return 1
    print(result[0])
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
    salt = bcrypt.gensalt(rounds=30,prefix=b'2b')
    hashed = bcrypt.kdf(
        password=bytes,
        salt=salt,
        desired_key_bytes=32,
        rounds=178
    )
    cursor = db.cursor()
    profImg = None
    isAdmin = 0
    print("pass: " + str(hashed))
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
        print(result[8].encode('utf-8'))
        print(password.encode('utf-8'))
        if str(hashed)==str(result[8]):
            return [username,result[2]]
        
    return [username,-1] # invalid login

def retrieveData(username):
    print("retrieve: "+ username)
    cursor = db.cursor()
    query = "SELECT * FROM web_user WHERE username = %s"
    cursor.execute(query,[username])
    result = cursor.fetchone()
    if result[3]:
        print("image found")
        image = base64.b64encode(result[3]).decode('utf-8')
    else:
        image = 0
        
    return result[1],result[6], image

def saveToDB(data, username):
    cursor = db.cursor()
    
    query = "SELECT user_id FROM web_user WHERE username=%s"
    cursor.execute(query,[username])
    result = cursor.fetchone()
    
    if not result:
        print("User not found. You shouldn't be here")
        return False
    
    user_id = result[0]
    
    '''
    query = "SELECT * FROM profile_img WHERE user_id = %s"
    cursor.execute(query, [user_id])
    result = cursor.fetchone()
    '''
    
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
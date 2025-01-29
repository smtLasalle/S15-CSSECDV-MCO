from app import db
import bcrypt

def getID(inc):
    cursor = db.cursor()
    print(cursor)
    query = "SELECT MAX(id_num) FROM web_user"
    try:
        cursor.execute("SELECT MAX(id_num) FROM web_user")
        print(cursor)
    except Exception as e:
        print("error somewhere", e)
    print('Getting ID')
    result = cursor.fetchone()
    print(result[0])
    if inc:
        return result[0]+1
    return result[0]

def newUserCheck(username,email,firstName,lastName,password,confirmPass,phoneNumber):
    #check if all fields have some text
    flag = 0
    if (password==confirmPass and bool(username) and checkEmail 
        and bool(firstName) and bool(lastName) and checkPhone):
        flag = 1
    
    cursor = db.cursor()
    query = "SELECT * FROM web_user WHERE username = %s OR email = %s"
    cursor.execute(query,(username,email))
    result = cursor.fetchone()
    if result:
        return 0
    return flag

def insertNewUser(idnum, username, firstName, lastName, email, password, phoneNumber, isParent):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes,salt)
    cursor = db.cursor()
    query = "INSERT INTO web_user (id_num, username, first_name, last_name, email, phone_number, password, isParent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (idnum, username, firstName, lastName, email, phoneNumber, hashed.decode('utf-8'), isParent))
    db.commit()

def checkPhone(phone):
    if "+63" in phone:
        if len(phone)==13:
            return 1
    return 0

def checkEmail(email):
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
    if valid:
        return 1
    return 0

def checkLogin(username, password):
    cursor = db.cursor()
    query = "SELECT * FROM web_user WHERE username = %s"
    cursor.execute(query,[username])
    result = cursor.fetchone()
    if result:
        print(result[6].encode('utf-8'))
        print(password.encode('utf-8'))
        if bcrypt.checkpw(password.encode('utf-8'),result[6].encode('utf-8')):
            if result[7]:
                return 2
            else:
                return 1
    return 0

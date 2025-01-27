from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bananaman6606",
    database="secdv"
)

# Route to serve the HTML form
@app.route('/')
def index():
    return render_template('new-user.html')  # Assumes 'index.html' is in the 'templates' folder

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    print("Bannaa")
    idnum = getID()
    username = request.form['username']
    email = request.form['email']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    #phoneNumber = request.form['phoneNumber']
    password = request.form['password']
    confirmPass = request.form['confirmPassword']

    #insert CHECK FOR REDUNDANCY
    if newUserCheck(username,email,firstName,lastName,password,confirmPass):
        cursor = db.cursor()
        query = "INSERT INTO web_user (id_num, username, first_name, last_name, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (idnum, username, firstName, lastName, email, password))
        db.commit()
        return "User Registered Successfully!"
    
    return "Username or Email Already Registered!"

def getID():
    cursor = db.cursor()
    query = "SELECT MAX(id_num) FROM web_user"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]+1

def newUserCheck(username,email,firstName,lastName,password,confirmPass):
    if (password==confirmPass and bool(username) and bool(email) 
        and bool(firstName) and bool(lastName)):
        flag = 1
    
    cursor = db.cursor()
    query = "SELECT * FROM web_user WHERE username = %s OR email = %s"
    cursor.execute(query,(username,email))
    result = cursor.fetchone()
    if result:
        return 0
    return 1

if __name__ == '__main__':
    app.run(debug=True)

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
print(db)

from app.controller import *
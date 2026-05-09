from flask import *
import hashlib
import secrets
import sqlite3

app = Flask(__name__)
app.secret_key = "evdemeleksokaktaiseseytandegiltanrinintakendisi"

DATABASE="Lib.db"

def saltink(len=12):
    return secrets.token_hex(len)

def dbconn(db):
    conn=sqlite3.connect(db)
    return conn

def hashink(pw,salt):
    return hashlib.sha256((pw,salt).encode('utf-8')).hexdigest()


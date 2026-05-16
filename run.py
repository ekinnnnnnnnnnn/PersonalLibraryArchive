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
    return hashlib.sha256((pw + salt).encode('utf-8')).hexdigest()

@app.route('/')
def index():
    if 'usersid' not in session:
        return redirect(url_for('login'))
    conn=dbconn(DATABASE)
    books=conn.execute("select * from books where userid=? order by id desc",
                       (session['usersid'],)).fetchall()
    conn.close()
    return render_template("index.html",
                            username=session['username'],
                            books=books)

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        pw=request.form['pw']
        salt=saltink()
        digest=hashink(pw,salt)
        conn=dbconn(DATABASE)
        try:
            conn.execute("insert into user(username,pw,salt) values (?,?,?)",
                         (username,digest,salt))
            conn.commit()
            conn.close()
            return redirect(url_for('login',success='regsok'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html",error="username is not available")
    return render_template("register.html",error=None)

@app.route('/login',methods=['GET', 'POST'])
def login():
    success=request.args.get('success')
    error=None
    if request.method=='POST':
        username=request.form['username']
        pw=request.form['pw']
        conn=dbconn(DATABASE)
        user=conn.execute("select id,pw,salt from user where username=?",
                          (username,)).fetchone()
        conn.close()
        if user and hashink(pw,user[2])==user[1]:
            session['usersid']=user[0]
            session['username']=username
            return redirect(url_for('index'))
        else:
            error="wrong username or pw"
    return render_template("login.html",error=error,success=success)

@app.route('/exit')
def exit():
    session.clear()
    return redirect(url_for('login'))

@app.route('/addbook',methods=['GET', 'POST'])
def addbook():
    if 'usersid' not in session:
        return redirect(url_for('login'))
    if request.method=='POST':
        bookname=request.form['bookname']
        author=request.form['author']
        type=request.form['type']
        status=request.form.get('status','not read yet')
        conn=dbconn(DATABASE)
        conn.execute("insert into books(userid,bookname,author,type,status) values (?,?,?,?,?)",
                     (session['usersid'],bookname,author,type,status))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template("addbook.html")










if __name__=="__main__":
    app.run(debug=True)
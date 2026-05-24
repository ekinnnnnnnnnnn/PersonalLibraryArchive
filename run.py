from flask import *
import hashlib
import secrets
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "evdemeleksokaktaiseseytandegiltanrinintakendisi"

DATABASE="Lib.db"
uploadFolder = os.path.join('static', 'uploads')
os.makedirs(uploadFolder, exist_ok=True)

def saltink(len=12):
    return secrets.token_hex(len)

def dbconn(db):
    conn=sqlite3.connect(db)
    conn.row_factory=sqlite3.Row
    return conn

def hashink(pw,salt):
    return hashlib.sha256((pw + salt).encode('utf-8')).hexdigest()

@app.route('/')
def index():
    if 'usersid' not in session:
        return redirect(url_for('login'))
    searchQuery = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    conn=dbconn(DATABASE)
    query = "select * from books where userid=?"
    params = [session['usersid']]
    if searchQuery:
        query += " and (bookname like ? or author like ?)"
        params.append(f"%{searchQuery}%")
        params.append(f"%{searchQuery}%") 
    if status:
        query += " and status=?"
        params.append(status)
    query += " order by id desc"

    books = conn.execute(query, params).fetchall()
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
        status=request.form.get('status','not read')
        rating=None
        if status=='read' and request.form.get('rating'):
            rating=int(request.form['rating'])
        tPage=request.form.get('tPage')
        rPage=request.form.get('rPage')
        try:
            total=int(tPage)
            read=int(rPage)
            if read>total:
                return render_template("addbook.html",error="read pages cannot exceed total pages")
        except ValueError:
            return render_template("addbook.html",error="total and read pages must be numbers")
        
        pdfFile = request.files.get('pdfFile')
        imageFile = request.files.get('imageFile')
        pdfFilename = None
        imageFilename = None
        if pdfFile and pdfFile.filename:
            pdfFilename = secure_filename(pdfFile.filename)
            pdfPath = os.path.join(uploadFolder, pdfFilename)
            pdfFile.save(os.path.join(uploadFolder, pdfFilename))

        if imageFile and imageFile.filename:
            imageFilename = secure_filename(imageFile.filename)
            imagePath = os.path.join(uploadFolder, imageFilename)
            imageFile.save(os.path.join(uploadFolder, imageFilename))

        conn=dbconn(DATABASE)
        conn.execute("insert into books(userid,bookname,author,type,status,rating,tPage,rPage,pdfF,imageF) values (?,?,?,?,?,?,?,?,?,?)",
                     (session['usersid'],bookname,author,type,status,rating,tPage,rPage,pdfFilename,imageFilename))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template("addbook.html")

@app.route('/deletebook/<int:bookid>')
def deleteBook(bookid):
    if 'usersid' not in session:
        return redirect(url_for('login'))
    conn=dbconn(DATABASE)
    conn.execute("delete from books where id=? and userid=?",
                 (bookid,session['usersid']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/book/<int:bookid>', methods=['GET', 'POST'])
def bookDetail(bookid):
    if 'usersid' not in session:
        return redirect(url_for('login'))
    conn=dbconn(DATABASE)
    book=conn.execute("select * from books where id=? and userid=?",
                      (bookid,session['usersid'])).fetchone()
    if request.method=='POST':
        formType=request.form.get('formType')
        if formType=='status':
            nstat=request.form.get('status')
            if nstat and nstat in ('not read','reading','read'):
                conn.execute("update books set status=? where id=? and userid=?",
                             (nstat,bookid,session['usersid']))
                if nstat!='read':
                    conn.execute("update books set rating=null where id=? and userid=?",
                                 (bookid,session['usersid']))
                conn.commit()
        elif formType=='rating':
            if book and book['status']=='read' and request.form.get('rating'):
                conn.execute("update books set rating=? where id=? and userid=?",
                             (int(request.form['rating']),bookid,session['usersid']))
                conn.commit()
        elif formType=='edit':
            bookname=request.form.get('bookname')
            author=request.form.get('author')
            btype=request.form.get('type')
            tPage=request.form.get('tPage')
            rPage=request.form.get('rPage')
            pdfFilename=book['pdfF']
            imageFilename=book['imageF']
            pdfFile=request.files.get('pdf')
            imageFile=request.files.get('image')
            if pdfFile and pdfFile.filename:
                pdfFilename=secure_filename(pdfFile.filename)
                pdfFile.save(os.path.join(uploadFolder, pdfFilename))
            if imageFile and imageFile.filename:
                imageFilename=secure_filename(imageFile.filename)
                imageFile.save(os.path.join(uploadFolder, imageFilename))
            conn.execute("update books set bookname=?,author=?,type=?,tPage=?,rPage=?,pdfF=?,imageF=? where id=? and userid=?",
                         (bookname,author,btype,tPage,rPage,pdfFilename,imageFilename,bookid,session['usersid']))
        elif formType=='comment':
            comm=request.form.get('comment','').strip() 
            conn.execute("insert into comments(bookid,userid,comment) values (?,?,?)",
                         (bookid,session['usersid'],comm))
            conn.commit()
        conn.close()
        return redirect(url_for('bookDetail',bookid=bookid))
    comments=conn.execute("select c.id,c.comment,c.date,u.username "
                          "from comments c join user u on c.userid=u.id "
                          "where c.bookid=? order by c.date desc ",
                          (bookid,)).fetchall()
    conn.close()
    return render_template("bookdetail.html",book=book,comments=comments)








if __name__=="__main__":
    app.run(debug=True)
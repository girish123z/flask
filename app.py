from flask import Flask, render_template,request,redirect,url_for,session,logging
import mysql.connector
from passlib.hash import sha256_crypt
from functools import wraps

mysqldb = mysql.connector.connect(host = "localhost",user="root",password="",database="student")

app = Flask(__name__)
xyz= ""
@app.route("/",methods =['GET','POST'])
def index():
    if request.method == "POST":
        name = request.form['name']
        cur = mysqldb.cursor(buffered=True)
        cur.execute("INSERT INTO ia (name)VALUES(%s)",[name])
        mysqldb.commit()
        cur.close()
        cur = mysqldb.cursor(buffered=True)
        cur.execute("SELECT * FROM ia")
        res = cur.fetchall()
        return render_template("index.html",res=res)
    cur = mysqldb.cursor(buffered=True)
    cur.execute("SELECT * FROM ia")
    res = cur.fetchall()
    if res:
        return render_template("index.html",res=res)
    return render_template("index.html")

@app.route('/edit/<string:id>',methods=['GET','POST'])
def edit(id):
    cur = mysqldb.cursor(buffered=True)
    cur.execute("SELECT * FROM ia where rollno = %s",[id])
    res = cur.fetchone()
    cur.close()
    if request.method =="POST":
        names = request.form['names']
        cur = mysqldb.cursor(buffered=True)
        cur.execute("UPDATE ia SET name =%s WHERE rollno=%s",(names,id))
        mysqldb.commit()
        cur.close()
        return redirect(url_for('index'))
    return render_template('edit.html',res=res)

@app.route('/delete/<string:id>',methods=['GET','POST'])
def delete(id):
    cur = mysqldb.cursor(buffered=True)
    cur.execute("DELETE FROM ia WHERE rollno = %s",[id])
    mysqldb.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cnum = request.form['cnum']
        uname = request.form['uname']
        password = sha256_crypt.encrypt(str(request.form['pass']))
        cur = mysqldb.cursor(buffered=True)
        cur.execute("INSERT INTO employee (empname,email,cno,uname,password) VALUES(%s,%s,%s,%s,%s)",(name,email,cnum,uname,password))
        mysqldb.commit()
        cur.close()
        print("register Successfull")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form['uname']
        password = request.form['password']
        cur = mysqldb.cursor(buffered=True)
        cur.execute("SELECT * FROM employee WHERE uname=%s",[uname])
        result = cur.fetchone()
        if result:
            passwords = result[5]
            if sha256_crypt.verify(password,passwords):
                session['logged_in'] = True
                session['username'] = uname
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('login'))
        else:
            print("Wrong Password")
            return redirect(url_for('login'))
    return render_template('login.html')

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/dashboard',methods = ['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__=='__main__':
    app.secret_key = '1234'
    app.run()

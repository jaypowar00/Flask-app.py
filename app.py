from flask import Flask,redirect,url_for,request,render_template,session,flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'redranger'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=1)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id",db.Integer,primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    passwd = db.Column(db.String(20))

    def __init__(self,username,email,passwd):
        self.username = username
        self.email = email
        self.passwd = passwd

@app.route('/',methods=["GET","POST"])
def index():
    if "username" in session:
        username = session["username"]
        return render_template('index.html',username=username)
    return render_template('index.html')

@app.route('/user',methods=["GET","POST"])
def user():
    if "username" in session:
        username = session["username"]
        email = session["email"]
        return render_template('user.html',username=username,email=email)
    return render_template('user.html')

@app.route('/register',methods=["GET","POST"])
def register():
    if "usename" not in session:
        if request.method == "POST":
            if "username" in request.form and "email" in request.form and "passwd" in request.form:
                username = request.form["username"]
                email = request.form["email"]
                passwd = request.form["passwd"]

                found_user = users.query.filter_by(username=username,email=email).first()
                if found_user:
                    return render_template('register.html',email=email)
                else:
                    usr = users(username,email,passwd)
                    db.session.add(usr)
                    db.session.commit()
                    return redirect(url_for('login'))
        else:
            username=session["username"]
            return render_template('register.html',username=username)
    else:
        email = session["email"]
        return render_template('register.html',username=username)
@app.route('/delete',methods=["GET","POST"])
def delete():
    username=None
    email=None
    if "username" in session:
        username = session["username"]
        email = session["email"]
    if request.method == "POST":
        passwd = request.form["passwd"]
        users.query.filter_by(username=username,email=email,passwd=passwd).delete()
        db.session.commit()
        session.pop("username",None)
        session.pop("email",None)
        return redirect(url_for('index'))
    else:
        return render_template('delete.html',username=username,email=email)

@app.route('/login',methods=["GET","POST"])
def login():
    if "username" in session:
        username = session["username"]
        return render_template('login.html',username=username)
    if request.method == "POST":
        username = request.form["username"]
        passwd = request.form["passwd"]
        found_user = users.query.filter_by(username=username,passwd=passwd).first()
        if found_user:
            session.permanent = True
            session["username"] = username
            session["email"] = found_user.email
            return redirect(url_for("user"))
        else:
            msg="No user found"
            return render_template('login.html',msg=msg)
    else:
        return render_template('login.html')

    
@app.route('/logout',methods=["POST","GET"])
def logout():
    username=None
    email=None
    if "username" in session:
        username = session["username"]
        email = session["email"]

    if request.method == "POST":
        session.pop("username",None)
        return redirect(url_for('login'))

    return render_template('logout.html',username=username,email=email)

if __name__ == "__main__":
    db.create_all()
    app.run()

import csv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from flask_sqlalchemy  import SQLAlchemy
from flask_bcrypt import Bcrypt
import datetime

app = Flask(__name__)

app.config["SECRET_KEY"] = "Hgdy73ghua7%^&g3gfd"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

db = SQLAlchemy(app)
loginmanager = LoginManager()
loginmanager.init_app(app)
bcrypt = Bcrypt(app)

first_row = []
with open("csv/city_day.csv", 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        first_row = row
        break

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    pwd = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255))

    def __repr__(self):
        return "<User '{}'>".format(self.email)

@loginmanager.user_loader
def load_user(id):
    return User.query.get(id)

def get_row(city, date):
    with open("csv/city_day.csv", 'r') as f:
        reader = csv.reader(f)
        for r in reader:
            if r[0] == city:
                if r[1] == date:
                    return [r]

def get_by_city(city):
    with open("csv/city_day.csv", 'r') as f:
        reader = csv.reader(f)
        r = []
        for row in reader:
            if row[0] == city:
                r.append(row)
        return r

def get_by_date(date):
    with open("csv/city_day.csv", 'r') as f:
        reader = csv.reader(f)
        r = []
        for row in reader:
            if row[1] == date:
                r.append(row)
        return r

@app.route('/')
def home():
    return redirect("/login")

@app.route('/signin', methods=["POST", "GET"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")
    else:
        username = request.form['username']
        email = request.form['email']
        pwd = request.form['password']
        cpwd = request.form['cpassword']

        usr = User.query.filter_by(email=email).first()

        if not usr:
            new_usr = User(username=username, email=email, pwd=bcrypt.generate_password_hash(pwd))
            db.session.add(new_usr)
            db.session.commit()
            login_user(new_usr, remember=True)
            flash("Successfully Signed in", "info")
            return redirect("/analyse")
        else:
            flash("There is already an account with that email", "error")
            return redirect("/signin")

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"]
        pwd = request.form["password"]

        usr = User.query.filter_by(email=email).first()

        if usr:
            if bcrypt.check_password_hash(usr.pwd, pwd):
                login_user(usr, remember=True)
                flash("Successfully Logged in", "info")
                return redirect("/analyse")
            else:
                flash("Wrong Password", "error")
                return redirect("/login")
        else:
            flash("User not found", "error")
            return redirect("/login")


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
       logout_user()
    return redirect("/login")

@app.route("/analyse", methods=["POST", "GET"])
def analyse():
    if current_user.is_authenticated:
        if request.method == "GET":
            return render_template("analyse.html")
        else:
            city = request.form["city"]
            date = request.form["date"]
            date = datetime.datetime.strptime(date, '%y-%m-%d')
            date = date.strftime("%d/%m/%y")
            print(date)
            if city != "" and date != "":
                d = get_row(city, date)
            elif city != "" and date == "":
                d = get_by_city(city)
            elif city == "" and date != "":
                d = get_by_date(date)
            d.insert(0, first_row)
            return render_template("result.html", data=d)
    else:
        return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_mysqldb import MySQL

app = Flask(__name__)

# ==========================
# SECRET KEY
# ==========================
app.config['SECRET_KEY'] = 'dev-secret-key-12345'

# ==========================
# CSRF PROTECTION
# ==========================
csrf = CSRFProtect(app)

# ==========================
# DATABASE CONFIG
# ==========================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'demo'

mysql = MySQL(app)

# ==========================
# FORMS
# ==========================
class RegistrationForm(FlaskForm):
    user_name = StringField("Username", validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo('password', message="Passwords must match")]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    user_name = StringField("Username", validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Login")


# ==========================
# REGISTER ROUTE
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user_name = form.user_name.data
        email = form.email.data
        password = form.password.data

        try:
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO login (user_name, email, password) VALUES (%s, %s, %s)",
                (user_name, email, password)
            )
            conn.commit()
            cursor.close()
            return redirect(url_for("login"))

        except Exception as e:
            return f"Database Error: {e}"

    return render_template("register.html", form=form)


# ==========================
# LOGIN ROUTE
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data

        try:
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM login WHERE user_name = %s AND password = %s",
                (user_name, password)
            )
            user = cursor.fetchone()
            cursor.close()

            if user:
                session["user"] = user_name  # store session
                return redirect(url_for("dashboard"))
            else:
                return "Invalid Username or Password"

        except Exception as e:
            return f"Database Error: {e}"

    return render_template("login.html", form=form)


# ==========================
# DASHBOARD (Protected)
# ==========================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


# ==========================
# LOGOUT ROUTE
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==========================
# OTHER ROUTES
# ==========================
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")


@app.route("/contactus")
def contactus():
    return render_template("contactus.html")


@app.route("/categories")
def categories():
    return render_template("categories.html")


@app.route("/jobs")
def jobs():
    return render_template("jobs.html")

@app.route("/form")
def form():
    return render_template("form.html")


# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    app.run(debug=True, port=8000)
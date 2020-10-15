from flask import Flask, render_template, redirect, url_for, flash
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e6040f19d063c7ea55a33765df99277c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pass.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    passwords = db.relationship('Password', backref = 'user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"


class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Password('{self.site}','{self.username}')"



@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == "__main__":
    app.run(debug=True)

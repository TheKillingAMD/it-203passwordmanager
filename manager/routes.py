from flask import render_template, redirect, url_for, flash, request
from manager import app, db, bcrypt
from manager.forms import RegistrationForm, LoginForm, UpdateAccountForm, PassForm
from manager.models import User, Password
from flask_login import login_user, current_user, logout_user, login_required
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import secrets
import matplotlib
import os
matplotlib.use('Agg')

def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 


def plot(string, random_hex):
    res = ''.join(format(ord(i), 'b') for i in string) 
    res = res.zfill(100)
    res = list(res)
    res = list(divide_chunks(res, 10))
    res = np.matrix(res)
    G = nx.from_numpy_matrix(res)
    fig = nx.draw(G)
    plt.savefig(random_hex, dpi = 75)
    return random_hex



# def BinaryToDecimal(binary): 
#     string = int(binary, 2) 
#     return string  

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        datas = Password.query.filter_by(user_id = current_user.id).first()
        image_file = datas.image_file + '.png'
        return render_template("home.html", datas=datas, image_file=image_file)
    else:
        return redirect(url_for('login'))

@app.route("/<int:image_id>")
def image():
    return 

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

@app.route("/password/new", methods=['GET', 'POST'])
@login_required
def new_pass():
    form = PassForm()
    if form.validate_on_submit():
        flash('Your Password has been added!', 'success')
        image_file = form.password.data
        random_hex = secrets.token_hex(8)
        picture_file = plot(image_file,random_hex)
        data = Password(site=form.site.data, username=form.username.data, password=form.password.data, user_id = current_user.id, image_file = picture_file )
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_pass.html', title='New Password', form=form)


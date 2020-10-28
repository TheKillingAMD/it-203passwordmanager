from flask import render_template, redirect, url_for, flash, request, abort
from manager import app, db, bcrypt, mail
from manager.forms import RegistrationForm, LoginForm, UpdateAccountForm, PassForm, RequestResetForm, ResetPasswordForm
from manager.models import User, Password
from flask_login import login_user, current_user, logout_user, login_required
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import secrets
import matplotlib
import os
import shutil
import sys
import cloudinary as Cloud
from flask_mail import Message
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
    plt.savefig(random_hex, dpi=75)
    return random_hex


# def BinaryToDecimal(binary):
#     string = int(binary, 2)
#     return string

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        datas = Password.query.filter_by(user_id=current_user.id).all()
        return render_template("home.html", datas=datas)
    else:
        return redirect(url_for('login'))


@app.route("/pass/<id>")
def password(id):
    if current_user.is_authenticated:
        data = Password.query.filter_by(id=id).first()
        return render_template("pass.html", data=data)
    else:
        return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
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
        picture_file = plot(image_file, random_hex) + ".png"
        original = sys.path[0] + "/" + picture_file
        target = sys.path[0] + "/manager/static/graph"
        shutil.move(original, target)
        image = "graph/" + picture_file
        data = Password(site=form.site.data, username=form.username.data,
                        password=form.password.data, user_id=current_user.id, image_file=image)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_pass.html', title='New Password', form=form, legend='New Post')


@app.route("/pass/<id>/edit", methods=['GET', 'POST'])
@login_required
def update_pass(id):
    data = Password.query.get_or_404(id)
    if data.user_id != current_user.id:
        abort(403)
    form = PassForm()
    if form.validate_on_submit():
        data.site = form.site.data
        data.username = form.username.data
        data.password = form.password.data
        os.remove("manager/static/" + data.image_file)
        image_file = form.password.data
        random_hex = secrets.token_hex(8)
        picture_file = plot(image_file, random_hex) + ".png"
        original = sys.path[0] + "/" + picture_file
        target = sys.path[0] + "/manager/static/graph"
        shutil.move(original, target)
        image = "graph/" + picture_file
        data.image_file = image
        db.session.commit()
        flash('Your Password has been updated!', 'success')
        return redirect(url_for('password', id=data.id))
    form.site.data = data.site
    form.username.data = data.username
    return render_template('create_pass.html', title='Update Password', form=form, )


@app.route("/pass/<id>/delete", methods=['POST'])
@login_required
def delete_pass(id):
    data = Password.query.get_or_404(id)
    if data.user_id != current_user.id:
        abort(403)
    os.remove("manager/static/" + data.image_file)
    db.session.delete(data)
    db.session.commit()
    flash('Your password has been deleted!', 'success')
    return redirect(url_for('home'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


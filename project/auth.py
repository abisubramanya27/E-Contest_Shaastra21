from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .class_orm import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    shaastraID = request.form.get('shaastraID')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(shaastraID=shaastraID).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.contest'))

@auth.route('/register')
def register():
    return render_template('register.html')

@auth.route('/register', methods=['POST'])
def register_post():
    shaastraID = request.form.get('shaastraID')
    password = request.form.get('password')
    name = request.form.get('name')
    email = request.form.get('email')
    confirm_pwd = request.form.get('confirm_password')

    user = User.query.filter_by(shaastraID = shaastraID).first() # if this returns a user, then the Shaastra ID already exists in database

    if user: # if a user is found, we want to redirect back to register page so user can try again
        flash('SHAASTRA ID already exists')
        return redirect(url_for('auth.register'))
    elif len(password) <= 5:
        flash('Password too small')
        return redirect(url_for('auth.register'))
    elif password != confirm_pwd:
        flash('Passwords didn\'t match')
        return redirect(url_for('auth.register'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(shaastraID=shaastraID, email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
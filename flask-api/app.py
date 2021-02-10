import json
import boto3

import flask
import SendgridService

from helpers import hash_password, generate_uid
from forms import RegistrationForm, LoginForm, ResetPasswordForm, RequestResetForm
from flask_lambda import FlaskLambda
from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask_wtf.csrf import CSRFProtect


app = FlaskLambda(__name__)
app.config.update(SECRET_KEY='kikakikakikakika')
csrf = CSRFProtect(app)
ddb = boto3.resource('dynamodb')
table = ddb.Table('userdatabase')


@app.route('/home', methods=['GET', 'POST'])
def home():

    return render_template('home_page.html')


@app.route('/register', methods=['GET', 'POST'])
def create_user():

    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', title='Register', form=form)

    else:
        if form.validate_on_submit():

            user_data = {'id': generate_uid(), 'fullname': form.username.data, 'email': form.email.data,
                         'password': hash_password(form.password.data)}
            if table.get_item(Key={'email': form.email.data}):
                flash('User with email address already exists', 'danger')
                return redirect('/Prod/register')

            table.put_item(Item=user_data)
            flash('user has been created', 'success')
            return redirect('/Prod/login')
        return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', title='Login', form=form)

    email = form.email.data
    password = hash_password(form.password.data)

    user_data = table.get_item(Key={'email': email})
    try:
        user_email = user_data['Item']['email']
        user_password = user_data['Item']['password']
    except:
        flash('User not found, please subscribe', 'danger')

        return render_template('login.html', title='Login', form=form)

    if user_email == email and user_password == password:
        return redirect('/Prod/home')
    flash('Email or password not right', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/reset', methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if request.method == 'GET':

        return render_template('reset_request.html', title='Reset Password', form=form)
    else:
        email = form.email.data
        response = table.get_item(Key={'email': email})
        if response:
            try:
                user_email = response['Item']['email']
                session['email'] = user_email
                SendgridService.send_email(user_email)
                flash('An email has been sent with instructions to reset your password.', 'info')
                return redirect('/Prod/login')
            except:
                flash('Incorrect email', 'danger')
                return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/password', methods=['GET', 'POST'])
def reset_pass():
    form = ResetPasswordForm()
    email = session.get('email')
    if request.method == 'GET':
        return render_template('reset_password.html', title='Reset Password', form=form)

    else:

        response = table.get_item(Key={'email': email})
        user = response['Item']
        user['password'] = hash_password(form.password.data)
        table.put_item(Item=user)
    return redirect('/Prod/login')







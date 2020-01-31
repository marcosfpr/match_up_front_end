from flask import request, render_template, redirect, flash, url_for
import requests

from .. import redirect_url
from . import auth_blueprint as bp
from config import BASE_API_URL
from .check import check_password_complexity
from security import Token


@bp.route("/login", methods=['GET', 'POST'])
@Token.auth_required
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.form
    request_data = {
        'username': data['username'],
        'password': data['password']
    }

    try:
        response = requests.post(BASE_API_URL + '/login', json=request_data)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'access_token' not in json and 'refresh_token' not in json:
        flash(json['error'])
        return render_template('login.html', username=request_data['username']), 401
    else:
        Token.update_token(json['access_token'], json['refresh_token'])

    return redirect(redirect_url())


@bp.route("/register", methods=['GET', 'POST'])
@Token.auth_required
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.form

    request_data = {
        'username': data['username'],
        'password': data['password'],
        'email': data['email']
    }

    check_password = check_password_complexity(data['password'], data['confirm-password'])
    if 'error' in check_password:
        flash(check_password['error'])
        return render_template('register.html',
                               username=request_data['username'],
                               email=request_data['email']), 401

    try:
        response = requests.post(BASE_API_URL + '/register', json=request_data)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'success' not in json:
        flash(json['error'])
        return render_template("register.html",
                               username=request_data['username'],
                               email=request_data['email']), 401

    return redirect(url_for('auth.login')), 200


@bp.route("/logout", methods=['GET'])
@Token.access_token_required
def logout():

    try:
        response = requests.post(BASE_API_URL+"/logout", headers=Token.get_header_access())
    except requests.exceptions.RequestException:
        return render_template("error.html")

    if 'success' not in response.json():
        return render_template("error.html")

    Token.access_token = None
    Token.refresh_token = None
    return redirect(url_for("auth.login"))

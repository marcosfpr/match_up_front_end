from flask import request, render_template, redirect, flash, url_for
import requests

from .. import redirect_url
from . import auth_blueprint as bp
from config import BASE_API_URL, BASE_FRONT_URL
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
        flash("[ERROR] " + json['error'])
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
        flash("[ERROR] " + check_password['error'])
        return render_template('register.html',
                               username=request_data['username'],
                               email=request_data['email']), 401

    try:
        response = requests.post(BASE_API_URL + '/register', json=request_data)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'success' not in json:
        flash("[ERROR] " + json['error'])
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


@bp.route("/change-password", methods=['GET', 'POST'])
@Token.access_token_required
def password_reset():
    if request.method == 'GET':
        return render_template("change-password.html")

    data = request.form
    request_data = {
        "actual_password": data['actual-password'],
        "new_password": data['new-password']
    }

    check_password = check_password_complexity(data['new-password'], data['confirm-password'])
    if 'error' in check_password:
        flash("[ERROR] " + check_password['error'])
        return redirect(url_for("home.profile"))

    try:
        response = requests.post(BASE_API_URL + '/change-password', headers=Token.get_header_access(),
                                 json=request_data)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'success' not in json:
        flash("[ERROR] " + json['error'])
    else:
        flash(json['success'])

    return redirect(url_for("home.profile"))


@bp.route("/recover", methods=['GET', 'POST'])
def password_recover():
    if request.method == 'GET':
        if "activation_key" in request.args:
            redirect(url_for("auth.choose_new_password", key=request.args.get('activation_key')))

        return render_template("recover.html")

    data = request.form
    request_data = {
        "email": data['email'],
        "username": data['username'],
        "link_prefix": BASE_FRONT_URL + "/recover"
    }

    try:
        response = requests.post(BASE_API_URL + '/recover', json=request_data)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'success' not in json:
        flash("[ERROR] " + json['error'])
    else:
        flash(json['success'])

    return render_template("recover.html")


@bp.route("/recover/<key>", methods=['GET', 'POST'])
def choose_new_password(key):

    params = {"activation_key": key}

    if request.method == 'GET':
        try:
            response = requests.get(BASE_API_URL + f'/recover/check', params=params)
        except requests.exceptions.RequestException:
            return render_template("error.html")

        json = response.json()

        if 'success' not in json:
            flash("[ERROR] " + json['error'])
            return render_template("recover.html")
        return render_template("choose-new-password.html", key=key)

    data = request.form
    request_data = {
        "password": data['password'],
    }

    check_password = check_password_complexity(data['password'], data['confirm-password'])
    if 'error' in check_password:
        flash("[ERROR] " + check_password['error'])
        return redirect(url_for("auth.choose_new_password", key=key))

    try:
        response = requests.post(BASE_API_URL + f'/recover/save', json=request_data, params=params)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'success' not in json:
        flash("[ERROR] " + json['error'])
    else:
        flash(json['success'])

    return redirect(url_for("auth.login"))

from flask import render_template, request, flash, redirect
import requests

from . import home_blueprint as bp
from security import Token
from config import BASE_API_URL


@bp.route("/", methods=['GET'])
@Token.access_token_required
def home():
    return render_template("index.html")


@bp.route("/about-us", methods=['GET'])
@Token.access_token_required
def about_us():
    return render_template("about_us.html")


@bp.route("/profile", methods=['GET', 'POST'])
@Token.access_token_required
def profile():

    if request.method == 'GET':
        try:
            response = requests.get(BASE_API_URL + f'/profile', headers=Token.get_header_access())
        except requests.exceptions.RequestException:
            return render_template("error.html")

        json = response.json()

        return render_template("profile.html", username=json['username'], email=json['email'], usage=json['usage'])

    data = request.form
    request_data = {
        "email": data['email'],
        "username": data['username']
    }

    try:
        response = requests.post(BASE_API_URL + f'/profile', headers=Token.get_header_access(),
                                json=request_data)
    except requests.exceptions.RequestException:
        return render_template("error.html")

    json = response.json()

    if 'error' in json:
        flash("[ERROR] " + json['error'])
    elif 'success' in json:
        flash(json['success'])

    return redirect(request.url)
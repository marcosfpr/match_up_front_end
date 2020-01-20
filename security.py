import requests
import functools

from flask import redirect, url_for

from config import BASE_API_URL


class Token:
    access_token = None
    refresh_token = None
    authorized = False
    revoked = False
    fresh = False

    @classmethod
    def check_token(cls):
        return f"access_token : {cls.access_token}\n refresh_token: {cls.refresh_token}"

    @classmethod
    def update_token(cls, access_token, refresh_token):
        cls.access_token = access_token
        cls.refresh_token = refresh_token

    @classmethod
    def get_header_access(cls):
        return {"Authorization": f"Bearer {cls.access_token}"}

    @classmethod
    def access_token_required(cls, func):
        @functools.wraps(func)
        def token(*args, **kwargs):
            try:
                response = requests.post(BASE_API_URL+"/check-access", headers=cls.get_header_access())
                if 'success' in response.json():
                    return func(*args, **kwargs)
                else:
                    cls.access_token = None
                    return redirect(url_for('auth.login'))
            except requests.exceptions.RequestException:
                return f"Connection denied"
        return token

    @classmethod
    def fresh_token_required(cls, func):
        @functools.wraps(func)
        def token(*args, **kwargs):
            try:
                response = requests.post(BASE_API_URL+"/check-fresh", headers=cls.get_header_access())
                if 'success' in response.json():
                    return func(*args, **kwargs)
                else:
                    cls.access_token = None
                    return redirect(url_for('auth.login'))
            except requests.exceptions.RequestException:
                return f"Connection denied"
        return token

    @classmethod
    def auth_required(cls, func):
        @functools.wraps(func)
        def login(*args, **kwargs):
            if cls.access_token:
                return redirect(url_for('home.home'))
            else:
                return func(*args, **kwargs)

        return login

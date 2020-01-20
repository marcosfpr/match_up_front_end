from flask import render_template

from . import home_blueprint as bp
from security import Token


@bp.route("/", methods=['GET'])
@Token.access_token_required
def home():
    return render_template("index.html")

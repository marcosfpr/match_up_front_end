from flask import Blueprint

search_blueprint = Blueprint('search', __name__)

from . import views
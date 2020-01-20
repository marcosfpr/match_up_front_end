from flask import Blueprint

collection_blueprint = Blueprint('collection', __name__)

from . import views
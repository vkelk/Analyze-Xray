from flask import Blueprint

xray = Blueprint('xray', __name__, template_folder='templates')

from . import views

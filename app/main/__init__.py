# define route by Blueprint

from flask import Blueprint

main = Blueprint('main', __name__)  # the 2 arg is Blueprint name and which package the Blueprint belong to

from . import views   # the route actually in the model views.py, import it that can \
                                # relevance route and Blueprint, must be imported at the end of Blueprint

from flask import Blueprint

website = Blueprint('website', 
                    __name__, 
                    static_folder='../static',
                    template_folder='../template')

from . import routes

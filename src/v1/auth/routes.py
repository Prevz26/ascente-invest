import logging
from flask import Blueprint
from flask_restful import Api, Resource

auth_bp = Blueprint("auth", __name__, url_prefix="/investment/auth")
api = Api(auth_bp)

# Setup logging
auth_logger = logging.getLogger(__name__)
auth_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/auth.log')
file_handler.setFormatter(formatter)
auth_logger.addHandler(file_handler)


class Registration(Resource):
    def __init__(self):
        pass

    def post(self):
        pass 


class Login(Resource):
    def __init__(self):
        pass


#register endpoints
api.add_resource(Registration, "/register")
api.add_resource(Login, "/login")
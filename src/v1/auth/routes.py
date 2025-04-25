import logging
from flask import Blueprint, request, make_response 
from flask_jwt_extended import jwt_required
from flask_restful import Api, Resource
from .service import auth_service
from utils.response import custom_response
from .schema import RegistrationSchema, LoginSchema
from utils.exceptions import AlreadyExistsError, NotFoundError, InvalidEmailPassword, TokenExpired
from pydantic import ValidationError 

auth_bp = Blueprint("auth", __name__, url_prefix="/investment")
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
        self.custom_response = custom_response 
        self.auth = auth_service


    def post(self):
        try:
            user = request.get_json()
            # auth_logger.info(user)
            validated_data = RegistrationSchema(**user).model_dump()
            del validated_data['confirm_password']
            auth_logger.info(validated_data)
            user = self.auth.create(**validated_data)
            return custom_response.success_response(
                data = user,
                status_code = 201
            )
        except AlreadyExistsError as e:
            auth_logger.error(str(e))
            return custom_response.error_response(
                message=str(e),
                status_code=409
            )
        
        except ValidationError as e:
            auth_logger.error(e.errors())
            return self.custom_response.validation_error(
                message= e.errors()
            )



class Login(Resource):
    def __init__(self):
        self.auth = auth_service
        self.custom_response = custom_response

    def post(self):
        user = request.get_json()
        if not user:
            return self.custom_response.error_response(
                message="No data provided",
                status_code=400
            )  
        try:
            data =  LoginSchema(**user).model_dump()
            auth_logger.info(data)
            username = data.get("username")
            password = data.get("password")
            user = self.auth.authenticate_user(username=username, password=password)

            access_token, refresh_token, role = self.auth.create_jwt(username)
            response = make_response(
                    self.custom_response.success_response(
                    data={
                        "access_token": access_token,
                    },
                    role=role)
                )
            response.set_cookie(
                    "refresh_token",
                    refresh_token,
                    httponly=True,
                    secure=True,  # Use HTTPS in production
                    samesite="Strict",  # Prevent CSRF
                    max_age=60 * 60 * 24 * 30 ) # 30 days
            return response
        except NotFoundError as e:
            auth_logger.error(str(e))
            return self.custom_response.not_found_error()
        except InvalidEmailPassword as e:
            auth_logger.error(str(e))
            return self.custom_response.forbidden_error(message="Incorrect password or email")
        except AlreadyExistsError as e:
            auth_logger.error(str(e))
            return self.custom_response.email_in_use_error()
        except ValidationError as e:
            auth_logger.error(e.error_count)
            return self.custom_response.validation_error(
                message= e.errors()
            )

class Refresh_Token(Resource):
    def __init__(self):
        self.auth = auth_service
        self.custom_response = custom_response

    @jwt_required( refresh=True)
    def post(self):
        refresh_token = request.headers.get("Authorization").split(" ")[1] # Extract token from header 

        if not refresh_token:
            auth_logger.error("No refresh token provided")
            return self.custom_response.error_response(
            message="No refresh token provided", 
            status_code=401
            )
        try:
            new_access_token = self.auth.validate_refresh_token(refresh_token)
            return self.custom_response.success_response(data=new_access_token)
        except TokenExpired as e:
            auth_logger.error(str(e))
            return self.custom_response.error_response(message="Invalid or expired refresh token", status_code=401)



#register endpoints
api.add_resource(Registration, "/register", endpoint="registration")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Refresh_Token, "/refresh-token")
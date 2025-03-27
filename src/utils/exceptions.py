from flask import Blueprint
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions
from .response import custom_response
import logging

exception_blueprint = Blueprint("exception", __name__)
exception_logger = logging.getLogger(__name__)

#create custom config for the exception logger
exception_logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/error.log')
console_handler = logging.StreamHandler()

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
exception_logger.addHandler(file_handler)
exception_logger.addHandler(console_handler)


@exception_blueprint.app_errorhandler(exceptions.BadRequest)
def bad_request_error_handler(e: exceptions.BadRequest):
    """
    Handles 400 Bad Request errors raised by Flask.
    Returns a 400 response with a JSON object containing the status 'error'
    and an 'errors' key containing the error description.
    :param e: The bad request exception
    :type e: werkzeug.exceptions.BadRequest
    """
    exception_logger.error(e.description)
    return custom_response.bad_request_error(message=e.description)


@exception_blueprint.app_errorhandler(exceptions.Unauthorized)
def unauthorized_error_handler(e: exceptions.Unauthorized):
    exception_logger.error(e.description)
    return custom_response.unauthorized_error(message=e.description)


@exception_blueprint.app_errorhandler(exceptions.Forbidden)
def forbidden_error_handler(e: exceptions.Forbidden):
    exception_logger.error(e.description)
    return custom_response.forbidden_error(message=e.description)

@exception_blueprint.app_errorhandler(exceptions.NotFound)
def not_found_error_handler(e: exceptions.NotFound):
    exception_logger.error(e.description)
    return custom_response.not_found_error(message=e.description)

@exception_blueprint.app_errorhandler(exceptions.HTTPException)
def http_error_handler(e: exceptions.HTTPException):
    exception_logger.error(e.description)
    return custom_response.base_error_response(message=e.description, status_code=e.code)

@exception_blueprint.app_errorhandler(IntegrityError)
def integrity_error_handler(e: IntegrityError):
    exception_logger.error(str(e))
    return custom_response.error_response(message='Integrity error: An object with this value already exists', status_code=e.code)

@exception_blueprint.app_errorhandler(exceptions.InternalServerError)
def internal_server_error_handler(e:exceptions.InternalServerError):
    
    exception_logger.error(e.description)
    return custom_response.base_error_response(message='Internal Server Error', status_code=500)

# @exception_blueprint.app_errorhandler(Exception)
# def internal_server_error(e: Exception):
#     exception_logger.error("Internal Server Error: %s", e)
#     return custom_response.server_error()

@exception_blueprint.app_errorhandler(ValidationError)
def validation_error_handler(e: ValidationError):
    exception_logger.error(str(e))
    return custom_response.validation_error(message=e.errors())

class Environment_Variable_Exception(Exception):
    def __init__ (self, variable_name):
        self.variable_name = variable_name
        super().__init__(f"Environment_Variable_Error: Variable missing {self.variable_name}")
        

class InUseError(Exception):
    pass

class TokenExpired(Exception):
    pass
class NotFoundError(Exception):
    pass

class AlreadyExistsError(Exception):
    pass

class InvalidEmailPassword(Exception):
    pass

class BadRequest(Exception):
    pass

class NotVerified(Exception):
    pass 

class EmailVerificationError(Exception):
    pass 



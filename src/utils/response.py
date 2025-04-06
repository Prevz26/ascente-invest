from typing import Optional, Tuple, Dict, Any



# Constants for error messages
EMAIL_IN_USE = "This email is already in use."
NOT_FOUND = "Not found!"
ID_OR_UNIQUE_ID_REQUIRED = "ID or Unique ID required!"
INVALID_CREDENTIALS = "Invalid Credentials!"
COULD_NOT_VALIDATE_CRED = "Could not validate credentials."
SUCCESS = "Success"
EXPIRED = "Token expired."
SERVER_ERROR = "An error occurred on the server"


class CustomResponse:
    """Custom response class for consistent API responses"""

    def _create_response(
        self,
        status: str,
        message: str,
        data: Optional[Any] = None,
        status_code: int = 200
    ) -> Tuple[Dict[str, Any], int]:
        
        response = {
            'status': status,
            'message': message,
            'data': data,
        }
        return response, status_code

    def success_response(
        self,
        message: str = SUCCESS,
        data: Optional[Any] = None,
        status_code: int = 200,
    ) -> Tuple[Dict[str, Any], int]:
        """Create a success response"""
        return self._create_response('success', message, data, status_code)
    


    def error_response(
        self,
        message: str,
        status_code: int,
        data: Optional[Any] = None
    ) -> Tuple[Dict[str, Any], int]:
        """Create an error response"""
        return self._create_response('error', message, data, status_code)

    def email_in_use_error(
        self,
        message: str = EMAIL_IN_USE
    ) -> Tuple[Dict[str, Any], int]:
        """409 Conflict - Email already in use"""
        return self.error_response(message, 409)

    def bad_request_error(
        self,
        message: str
    ) -> Tuple[Dict[str, Any], int]:
        """400 Bad Request"""
        return self.error_response(message, 400)

    def unauthorized_error(
        self,
        message: str = COULD_NOT_VALIDATE_CRED
    ) -> Tuple[Dict[str, Any], int]:
        """401 Unauthorized"""
        return self.error_response(message, 401)

    def forbidden_error(
        self,
        message: str = 'Permission denied'
    ) -> Tuple[Dict[str, Any], int]:
        """403 Forbidden"""
        return self.error_response(message, 403)

    def not_found_error(
        self,
        message: str = NOT_FOUND
    ) -> Tuple[Dict[str, Any], int]:
        """404 Not Found"""
        return self.error_response(message, 404)

    def server_error(
        self,
        message: str = SERVER_ERROR
    ) -> Tuple[Dict[str, Any], int]:
        """500 Internal Server Error"""
        return self.error_response(message, 500)
    
    def json_missing_error(
        self,
        message: str = 'JSON is missing'
        ) -> Tuple[Dict[str, Any], int]:
        """400 Bad Request - JSON is missing"""
        return self.error_response(message, 400)
    def validation_error(
        self,
        message: str 
    ) -> Tuple[Dict[str, Any], int]:
        """422 Unprocessable Entity - Validation error"""
        return self.error_response(message, 422)

# Single instance for import
custom_response = CustomResponse()
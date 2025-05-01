from functools import wraps
from v1.auth.service import auth_service
from utils.response import custom_response



def admin_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = auth_service.get_current_user()
            user_id = current_user.unique_id
            admin = auth_service.check_admin(user_id)
            if not admin:
                return custom_response.unauthorized_error(
                    message="Not authorized"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def user_only():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = auth_service.get_current_user()
            user_id = current_user.unique_id
            user = auth_service.check_user(user_id)
            if not user:
                return custom_response.unauthorized_error(
                    message="Not authorized"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator





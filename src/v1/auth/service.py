# This is the service module for the auth, contains auth specific methods like login, password hashing, current users etc

import datetime
from utils.dependency import db
from utils.exceptions import NotFoundError, AlreadyExistsError, InvalidEmailPassword, BadRequest, TokenExpired, ServerError
import utils.dependency
import logging 
from flask_jwt_extended import create_access_token, get_jwt_identity, create_refresh_token
from v1.profiles.models import User, RefreshToken
from v1.plans.models import Wallet
from sqlalchemy import and_, or_, func

# Setup logging
auth_logger = logging.getLogger(__name__)
auth_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/auth.log')
file_handler.setFormatter(formatter)
auth_logger.addHandler(file_handler)

class AuthService():
    """
    This is the service module for the auth, contains auth specific methods like login, password hashing, current users etc.
    """
    def __init__(self, model=None):
        """
        Initializes the service with a model.

        Args:
            model: the model to use for the service
        """
        self.model = User
        self.db = db.session
        
    @classmethod
    def clean_email(cls, email: str) -> str:
        return email.strip().lower()
    

    def create(self, **request_data: dict):
        auth_logger.info(f"Creating new user with email: {request_data.get('email')}")

        clean_mail = self.clean_email(request_data["email"])
        auth_logger.debug(f"Cleaned email: {clean_mail}")

        # Checks for an existing user
        self.existing_users = self.db.query(self.model).filter_by(email=clean_mail).first()
        if self.existing_users:
            auth_logger.warning(f"User with email {clean_mail} already exists")
            raise AlreadyExistsError("User already exists")

        # If the request data validates, hashes the password
        request_data['password'] = self.hash_password(request_data['password'])
        auth_logger.debug("Password hashed successfully")
        
        # Stores the user data in the database
        user = self.model(**request_data)
        user.wallet = Wallet()
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            auth_logger.info(f"Successfully created user with ID: {user.unique_id}")
        except Exception as e:
            self.db.rollback()
            auth_logger.error(f"Failed to create user: {str(e)}")
            raise ServerError("An error occured on the server")
        return user.to_dict()
    
    def create_jwt(self, username):
        self.existing_users = self.db.query(self.model).filter(self.model.username == username.lower()).first()
        auth_logger.info(f"existing user: {self.existing_users}")
        if not self.existing_users:
            raise NotFoundError("User not found")
        access_token = create_access_token(
            identity=self.existing_users.unique_id,  
            additional_claims={
                "email": self.existing_users.email
            },
            expires_delta=datetime.timedelta(hours=2)  # Token expiration
        )
        refresh_token = create_refresh_token(identity=self.existing_users.unique_id)

        #store refresh token in db
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
        new_refresh_token = RefreshToken(user_id=str(self.existing_users.unique_id), token=refresh_token, expires_at=expires_at)
        db.session.add(new_refresh_token)
        db.session.commit()
        return access_token, refresh_token
    
    def validate_refresh_token(self, refresh_token):
        user_id = self.get_current_user()
        token_entry = self.db.query(RefreshToken).filter_by(token=refresh_token, user_id=str(user_id), revoked=False).first()

        if not token_entry or token_entry.expires_at < datetime.datetime.now(datetime.timezone.utc):
            raise TokenExpired("Token has expired")
        
        # Generate new access token
        new_access_token = create_access_token(identity=user_id)
        return new_access_token
    

    def authenticate_user(self, username: str, password: str):
        lowercase_str = username.lower()
        query = self.db.query(self.model)
        user = query.filter(func.lower(self.model.username) == lowercase_str).first()

        if user is None:
            auth_logger.info("User not found")
            raise NotFoundError("User not found")
        
        auth_logger.info(f"User found: {user}")
        if not self.verify_password(hashed_password=user.password, password=password):
            raise InvalidEmailPassword("Invalid password or email")
        if user:
            auth_logger.info("User authenticated")
            return user.to_dict()
    
    
    def hash_password(self, password: str) -> str:
        return utils.dependency.bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, hashed_password: str, password: str) -> bool:
        return utils.dependency.bcrypt.check_password_hash(hashed_password, password)
    
    def change_password(self, request_data):
        # schema_data = password_reset_schema.load(request_data)
        user = self.authenticate_user(email=request_data['email'], password=request_data['old_password'])

        if request_data['new_password'] != request_data['confirm_password']:
            raise BadRequest('Passwords do not match')

        if request_data['new_password'] == request_data['old_password']:
            raise BadRequest('New password cannot be the same as the old password')

        user.password = self.hash_password(request_data['new_password'])
        self.db.commit()

    def get_current_user(self):
        user_unique_id = get_jwt_identity()
        
        auth_logger.info(user_unique_id)
        query = self.db.query(self.model)
        user = query.filter_by(unique_id=user_unique_id).first()
        auth_logger.info(f"User found: {user}")
        if user is None:
            auth_logger.error("User not found")
            raise NotFoundError("Not found")
        return user

    def check_admin(self, user_id):
        admin = self.db.query(self.model).filter(
            and_(self.model.unique_id==user_id, self.model.is_admin ==True)
            ).first()
        return admin
        


auth_service = AuthService()
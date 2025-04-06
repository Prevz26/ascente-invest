#this seervice handles the operations of user profiles
from v1.profiles.models import User
from v1.auth.service import auth_service 
from utils.dependency import db 
from utils.exceptions import NotFoundError, BadRequest, DatabaseError
import logging 
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
profile_logger = logging.getLogger(__name__)
profile_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/profile.log')
file_handler.setFormatter(formatter)
profile_logger.addHandler(file_handler)

class ProfileService():
    def __init__(self):
        self.model = User
        self.db = db.session
        self.auth = auth_service

    def fetch_details(self):
        try:
            current_user = self.auth.get_current_user()
            if not current_user:
                profile_logger.error("No current user found")
                raise NotFoundError("No authenticated user found")

            user_details = self.db.query(self.model).filter_by(id=current_user.id).first()
            if not user_details:
                profile_logger.error(f"No details found for user {current_user.id}")
                raise ValueError("User details not found")

            profile_logger.info(f"Successfully fetched details for user {current_user.id}")
            return user_details.to_dict()

        except Exception as e:
            profile_logger.error(f"Error fetching user details: {str(e)}")
            raise

    def update_profile(self, update_data: dict):
        profile_logger.info(update_data)
        try:
            current_user = self.auth.get_current_user()
            if not current_user:
                profile_logger.error("No current user found")
                raise NotFoundError("No authenticated user found")

            user = self.db.query(self.model).filter_by(id=current_user.id).first()
            if not user:
                profile_logger.error(f"No user found with id {current_user.id}")
                raise NotFoundError("User not found")

            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            self.db.commit()
            profile_logger.info(f"Successfully updated profile for user {current_user.id}")
            return user.to_dict()

        except SQLAlchemyError as e:
            self.db.rollback()
            profile_logger.error(f"Error updating user profile: {str(e)}")
            raise DatabaseError(str(e))
    
profile_service = ProfileService()
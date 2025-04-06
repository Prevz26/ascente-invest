import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, Api
from  utils.response import custom_response
from utils.exceptions import DatabaseError, NotFoundError, BadRequest
from .service import profile_service
from .schema import LoadProfileSchema, DumpProfileSchema


profile_bp = Blueprint("profile", __name__, url_prefix="/investment")
api = Api(profile_bp)

# Setup logging
auth_logger = logging.getLogger(__name__)
auth_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/profile.log')
file_handler.setFormatter(formatter)
auth_logger.addHandler(file_handler)

class GetProfile(Resource):
    def __init__(self):
        self.custom_response = custom_response 
        self.profile = profile_service

    @jwt_required()
    def get(self):
        try:
            user_details = self.profile.fetch_details()
            validated_data = DumpProfileSchema(**user_details).model_dump()
            return self.custom_response.success_response(
                message="Profile successfully fetched",
                data = validated_data
            )
        except NotFoundError as e:
            auth_logger.error(str(e))
            return self.custom_response.not_found_error()
        

class UpdateDeleteProfile(Resource):
    def __init__(self):
        self.custom_response = custom_response 
        self.profile = profile_service

    @jwt_required()
    def patch(self):
        try:
            update_data = request.get_json()
            auth_logger.info(f"Received profile update request with data: {update_data}")
            
            validated_data = LoadProfileSchema(**update_data).model_dump(exclude_unset=True)
            auth_logger.debug(f"Validated update data: {validated_data}")

            updated_profile = self.profile.update_profile(validated_data)
            auth_logger.info(f"Successfully updated profile for user")

            response_data = LoadProfileSchema(**updated_profile).model_dump()
            return self.custom_response.success_response(
                message="Profile successfully updated",
                data=response_data
            )
        except NotFoundError as e:
            auth_logger.error(f"Profile update failed - not found error: {str(e)}")
            return self.custom_response.not_found_error()
        except DatabaseError as e:
            auth_logger.error(f"Profile update failed - bad request: {str(e)}")
            return self.custom_response.error_response(
                message="Database Error",
                status_code=500
            )


    def delete(self):
        pass 

#add routes
api.add_resource(GetProfile, "/profile")
api.add_resource(UpdateDeleteProfile, "/profile")
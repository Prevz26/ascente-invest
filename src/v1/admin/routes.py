import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restful import Api, Resource
from .service import AdminService
from utils.response import custom_response
from v1.plans.schema import RequestPlan, ListResponsePlan, ResponsePlan, UpdatePlan
from utils.exceptions import AlreadyExistsError, ServerError, NotFoundError
from pydantic import ValidationError
from utils.decorators import admin_required
from sqlalchemy.exc import SQLAlchemyError
from utils.log import get_log_path
admin_bp = Blueprint("admin", __name__, url_prefix="/investment/admin")
api = Api(admin_bp)

# Setup logging
admin_logger = logging.getLogger(__name__)
admin_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(get_log_path('admin.log'))
file_handler.setFormatter(formatter)
admin_logger.addHandler(file_handler)


class CreatePlan(Resource):
    def __init__(self):
        self.admin_service = AdminService()
        self.custom_response = custom_response

    @jwt_required()
    @admin_required()
    def post(self):
        try:
            plan_data = request.get_json()
            admin_logger.info(plan_data)
            validated_data = RequestPlan(**plan_data).model_dump()
            admin_logger.info(f"Creating new plan with data: {validated_data}")
            
            new_plan = self.admin_service.create_plan(**validated_data)
            response_data = ResponsePlan(**new_plan).model_dump()
            return self.custom_response.success_response(
                status_code = 201,
                data=response_data,
                message="Plan created successfully"
            )
        except AlreadyExistsError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message=str(e),
                status_code=409
            )
        except ValidationError as e:
            admin_logger.error(e.errors())
            return self.custom_response.validation_error(
                message=e.errors()
            )
        except ServerError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message=str(e),
                status_code=500
            )


class ViewAllPlans(Resource):
    def __init__(self):
        self.admin_service = AdminService()
        self.custom_response = custom_response

    @jwt_required()
    def get(self):
        try:
            plans = self.admin_service.fetch_all_plans()
            response = ListResponsePlan(plans=plans).model_dump()
            return self.custom_response.success_response(
                data=response,
                message="Plans retrieved successfully"
            )
        except ServerError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message="Failed to retrieve plans",
                status_code=500
            )

class GetUpdateDeletePlan(Resource):
    def __init__(self):
        self.admin_service = AdminService()
        self.custom_response = custom_response

    @jwt_required()
    def get(self, id):
        try:
            plan = self.admin_service.fetch_single_plans(id)
            response_data = ResponsePlan(**plan).model_dump()
            return self.custom_response.success_response(
                data=response_data,
                message="Plan retrieved successfully"
            )
        except NotFoundError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message=str(e),
                status_code=404
            )
        except ServerError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message="Failed to retrieve plan",
                status_code=500
            )

    @jwt_required()
    @admin_required()
    def patch(self, id):
        try:
            plan_data = request.get_json()
            validated_data = UpdatePlan(**plan_data).model_dump(exclude_unset=True)
            admin_logger.info(f"Updating plan {id} with data: {validated_data}")
            
            updated_plan = self.admin_service.update_plan(id, **validated_data)
            response_data = ResponsePlan(**updated_plan).model_dump()
            return self.custom_response.success_response(
                data=response_data,
                message="Plan updated successfully"
            )
        except NotFoundError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message=str(e),
                status_code=404
            )
        except ValidationError as e:
            admin_logger.error(e.errors())
            return self.custom_response.validation_error(
                message=e.errors()
            )
        except ServerError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message=str(e),
                status_code=500
            )

    @jwt_required()
    @admin_required()
    def delete(self, id):
        try:
            self.admin_service.delete_plan(id)
            return self.custom_response.success_response(
                message="Plan deleted successfully",
                status_code=200
            )
        except NotFoundError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message=str(e),
                status_code=404
            )
        except ServerError as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message=str(e),
                status_code=500
            )



class ViewUsers(Resource):
    def __init__(self):
        self.admin_service = AdminService()
        self.custom_response = custom_response

    @jwt_required()
    def get(self):
        try:
            users = self.admin_service.fetch_all_users()
            return self.custom_response.success_response(
                data=users,
                message="Users retrieved successfully"
            )
        except Exception as e:
            admin_logger.error(str(e))
            return self.custom_response.error_response(
                message="Failed to retrieve users",
                status_code=500
            )


# Register endpoints
api.add_resource(CreatePlan, "/plan", endpoint="create_plan")
api.add_resource(ViewAllPlans, "/plans", endpoint="view_plans")
api.add_resource(GetUpdateDeletePlan, "/plan/<int:id>", endpoint="manage_plan")

api.add_resource(ViewUsers, "/users", endpoint="view_users")
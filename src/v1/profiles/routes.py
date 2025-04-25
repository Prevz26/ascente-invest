import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, Api
from  utils.response import custom_response
from utils.exceptions import DatabaseError, NotFoundError, BadRequest, ServerError
from .service import profile_service
from .schema import LoadProfileSchema, DumpProfileSchema
from v1.plans.service import wallet_service, investment_service, user_plan_service
from v1.plans.schema import MakePayment, SuccessCallback, ResponsePlan, ListResponsePlan



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


class GetWallet(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.wallet = wallet_service

    @jwt_required()
    def get(self):
        try:
            balance = self.wallet.check_balance()
            return self.custom_response.success_response(
                message="Wallet balance fetched successfully",
                data={"balance": balance}
            )
        except NotFoundError:
            auth_logger.error("Wallet not found")
            return self.custom_response.not_found_error()



class FetchAllPlans(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.plan = user_plan_service

    @jwt_required()
    def get(self):
        try:
            plans = self.plan.get_all_plans()
            return self.custom_response.success_response(
                message="Plans fetched successfully",
                data=ListResponsePlan(plans=plans).model_dump()
            )
        except NotFoundError:
            auth_logger.error("Plans not found")
            return self.custom_response.not_found_error()

class FetchSinglePlan(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.plan = user_plan_service

    @jwt_required()
    def get(self, plan_id):
        try:
            plan = self.plan.get_single_plan(plan_id)
            return self.custom_response.success_response(
                message="Plan fetched successfully",
                data=ResponsePlan(**plan).model_dump()
            )
        except NotFoundError:
            auth_logger.error("Plan not found")
            return self.custom_response.not_found_error()
class BuyPlan(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.wallet = wallet_service
        self.plan = user_plan_service

    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            validated_data = MakePayment(**data).model_dump()
            auth_logger.info(f"Received plan purchase request with data: {validated_data}")
            amount = validated_data.get('amount')
            token = validated_data.get('token')
            plan_id = validated_data.get("plan_id")
            
            if not amount or not token or not plan_id:
                return self.custom_response.bad_request_error(
                    message= "Amount, token, plan_id are required"
                )

            address = self.plan.buy_plan_directly(plan_id=plan_id, token=token, amount=amount)
            return self.custom_response.success_response(
                message="Plan Payment initiated",
                data={"payment_address": address}
            )
        except BadRequest as e:
            auth_logger.error(f"Invalid request: {str(e)}")
            return self.custom_response.bad_request_error()
        except ServerError as e:
            auth_logger.error(f"Server error: {str(e)}")
            return self.custom_response.error_response(
                message="Server Error",
                status_code=500
            )

class Webhook(Resource):
    def __init__(self):
        self.callback = user_plan_service

    def post(self):
        investment_id = request.args.get('investment_id')
        data = request.get_json()
        callback = self.callback.handle_callback(investment_id, **data)
        auth_logger.info(investment_id) 
        auth_logger.info(data) 
        return "ok"


class Transcation(Resource):
    pass 

class Fetch_paid_plan(Resource):
    pass 
#add routes
api.add_resource(GetProfile, "/profile")
api.add_resource(UpdateDeleteProfile, "/profile")
api.add_resource(Webhook, "/webhook")
api.add_resource(GetWallet, "/wallet")
api.add_resource(BuyPlan, "/plan/buy")
api.add_resource(FetchAllPlans, "/plans")
api.add_resource(FetchSinglePlan, "/plan/<int:plan_id>")
import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, Api
from  utils.response import custom_response
from utils.exceptions import DatabaseError, NotFoundError, BadRequest, ServerError
from utils.log import get_log_path
from .service import profile_service
from .schema import LoadProfileSchema, DumpProfileSchema
from v1.plans.service import wallet_service, investment_service, user_plan_service
from v1.plans.schema import MakePayment, SuccessCallback, ResponsePlan, ListResponsePlan, CheckPayment, DailyProfit, Balance
from utils.decorators import user_only



profile_bp = Blueprint("profile", __name__, url_prefix="/investment")
api = Api(profile_bp)

# Setup logging
auth_logger = logging.getLogger(__name__)
auth_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(get_log_path('profile.log'))
file_handler.setFormatter(formatter)
auth_logger.addHandler(file_handler)

class GetProfile(Resource):
    def __init__(self):
        self.custom_response = custom_response 
        self.profile = profile_service

    @jwt_required()
    @user_only()
    def get(self):
        auth_logger.info("GetProfile: GET /profile called")
        try:
            user_details = self.profile.fetch_details()
            auth_logger.info("GetProfile: User details fetched from service")
            validated_data = DumpProfileSchema(**user_details).model_dump()
            auth_logger.info("GetProfile: User details validated and dumped")
            return self.custom_response.success_response(
                message="Profile successfully fetched",
                data = validated_data
            )
        except NotFoundError as e:
            auth_logger.error(f"GetProfile: NotFoundError - {str(e)}")
            return self.custom_response.not_found_error()
        

class UpdateDeleteProfile(Resource):
    def __init__(self):
        self.custom_response = custom_response 
        self.profile = profile_service

    @jwt_required()
    @user_only()
    def patch(self):
        auth_logger.info("UpdateDeleteProfile: PATCH /profile called")
        try:
            update_data = request.get_json()
            auth_logger.info(f"UpdateDeleteProfile: Received profile update request with data: {update_data}")
            
            validated_data = LoadProfileSchema(**update_data).model_dump(exclude_unset=True)
            auth_logger.debug(f"UpdateDeleteProfile: Validated update data: {validated_data}")

            updated_profile = self.profile.update_profile(validated_data)
            auth_logger.info(f"UpdateDeleteProfile: Successfully updated profile for user")

            response_data = LoadProfileSchema(**updated_profile).model_dump()
            auth_logger.info("UpdateDeleteProfile: Response data prepared")
            return self.custom_response.success_response(
                message="Profile successfully updated",
                data=response_data
            )
        except NotFoundError as e:
            auth_logger.error(f"UpdateDeleteProfile: Profile update failed - not found error: {str(e)}")
            return self.custom_response.not_found_error()
        except DatabaseError as e:
            auth_logger.error(f"UpdateDeleteProfile: Profile update failed - bad request: {str(e)}")
            return self.custom_response.error_response(
                message="Database Error",
                status_code=500
            )

    def delete(self):
        auth_logger.info("UpdateDeleteProfile: DELETE /profile called (not implemented)")
        pass 


class GetWallet(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.wallet = wallet_service

    @jwt_required()
    @user_only()
    def get(self):
        auth_logger.info("GetWallet: GET /wallet called")
        try:
            balance = self.wallet.check_balance()
            auth_logger.info(f"GetWallet: Wallet balance fetched: {balance}")
            validated_data = Balance(balance=balance).model_dump()
            auth_logger.info("GetWallet: Wallet balance validated and dumped")
            return self.custom_response.success_response(
                message="Wallet balance fetched successfully",
                data=validated_data
            )
        except NotFoundError as e:
            auth_logger.error(f"GetWallet: NotFoundError - {str(e)}")
            return self.custom_response.not_found_error()



class FetchAllPlans(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.plan = user_plan_service

    @jwt_required()
    def get(self):
        auth_logger.info("FetchAllPlans: GET /plans called")
        try:
            plans = self.plan.get_all_plans()
            auth_logger.info(f"FetchAllPlans: Plans fetched: {plans}")
            return self.custom_response.success_response(
                message="Plans fetched successfully",
                data=ListResponsePlan(plans=plans).model_dump()
            )
        except NotFoundError:
            auth_logger.error("FetchAllPlans: Plans not found")
            return self.custom_response.not_found_error()

class FetchSinglePlan(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.plan = user_plan_service

    @jwt_required()
    def get(self, plan_id):
        auth_logger.info(f"FetchSinglePlan: GET /plan/{plan_id} called")
        try:
            plan = self.plan.get_single_plan(plan_id)
            auth_logger.info(f"FetchSinglePlan: Plan fetched: {plan}")
            return self.custom_response.success_response(
                message="Plan fetched successfully",
                data=ResponsePlan(**plan).model_dump()
            )
        except NotFoundError:
            auth_logger.error(f"FetchSinglePlan: Plan {plan_id} not found")
            return self.custom_response.not_found_error()
class BuyPlan(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.wallet = wallet_service
        self.plan = user_plan_service

    @jwt_required()
    @user_only()
    def post(self):
        auth_logger.info("BuyPlan: POST /plan/buy called")
        try:
            data = request.get_json()
            auth_logger.info(f"BuyPlan: Received plan purchase request with data: {data}")
            validated_data = MakePayment(**data).model_dump()
            auth_logger.info(f"BuyPlan: Validated plan purchase data: {validated_data}")
            amount = validated_data.get('amount')
            token = validated_data.get('token')
            plan_id = validated_data.get("plan_id")
            
            if not amount or not token or not plan_id:
                auth_logger.warning("BuyPlan: Missing required fields in request")
                return self.custom_response.bad_request_error(
                    message= "Amount, token, plan_id are required"
                )

            address = self.plan.buy_plan_directly(plan_id=plan_id, token=token, amount=amount)
            auth_logger.info(f"BuyPlan: Plan payment initiated, payment details: {address}")
            return self.custom_response.success_response(
                message="Plan Payment initiated",
                data={"payment_details": address}
            )
        except BadRequest as e:
            auth_logger.error(f"BuyPlan: Invalid request: {str(e)}")
            return self.custom_response.bad_request_error()
        except ServerError as e:
            auth_logger.error(f"BuyPlan: Server error: {str(e)}")
            return self.custom_response.error_response(
                message=str(e),
                status_code=500
            )

class Webhook(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.callback = user_plan_service

    def post(self):
        auth_logger.info("Webhook: POST /webhook called")
        try:
            transaction_id = request.args.get('transaction_id')
            if not transaction_id:
                auth_logger.error("Webhook: No transaction_id provided")
                return self.custom_response.bad_request_error(
                    message="Transaction ID is required"
                )
                
            data = request.get_json()
            auth_logger.info(f"Webhook: Received webhook data: {data} for transaction_id: {transaction_id}")
            validated_data = SuccessCallback(**data).model_dump()
            auth_logger.info(f"Webhook: Validated webhook data: {validated_data}")
            callback = self.callback.handle_callback(transaction_id, **validated_data)
            auth_logger.info(f"Webhook: Webhook processed for transaction_id: {transaction_id}")
            auth_logger.info(f"Webhook: Webhook data: {data}")
            
            if callback:
                auth_logger.info("Webhook: Callback returned successfully")
                return "ok"

        except BadRequest as e:
            auth_logger.error(f"Webhook: Bad request error: {str(e)}")
            return self.custom_response.bad_request_error()
        except ServerError as e:
            auth_logger.error(f"Webhook: Server error: {str(e)}")
            return self.custom_response.error_response(
            message=str(e),
            status_code=500
            )
        except NotFoundError as e:
            auth_logger.error(f"Webhook: Unexpected error in webhook: {str(e)}")
            return self.custom_response.not_found_error(
            message=str(e)
            )

class CheckPaymentStatus(Resource):
    def __init__(self):
        self.custom_response = custom_response
        self.plan = user_plan_service
    
    @jwt_required()
    def get(self, transaction_id):
        auth_logger.info(f"CheckPaymentStatus: GET /payment-status/{transaction_id} called")
        try:
            data = self.plan.check_payment_status(transaction_id)
            auth_logger.info(f"CheckPaymentStatus: Payment status fetched: {data}")
            validated_data = CheckPayment(**data).model_dump()
            auth_logger.info("CheckPaymentStatus: Payment status validated and dumped")
            return self.custom_response.success_response(
                message="Payment status fetched successfully",
                data=validated_data
            )
        except NotFoundError:
            auth_logger.error(f"CheckPaymentStatus: Transaction {transaction_id} not found")
            return self.custom_response.not_found_error()
        except ServerError as e:
            auth_logger.error(f"CheckPaymentStatus: Server error: {str(e)}")
            return self.custom_response.error_response(
                message=str(e),
                status_code=500
            )

#add routes
api.add_resource(GetProfile, "/profile")
api.add_resource(UpdateDeleteProfile, "/profile")
api.add_resource(Webhook, "/webhook")
api.add_resource(GetWallet, "/wallet")
api.add_resource(BuyPlan, "/plan/buy")
api.add_resource(FetchAllPlans, "/plans")
api.add_resource(FetchSinglePlan, "/plan/<int:plan_id>")
api.add_resource(CheckPaymentStatus, "/payment-status/<string:transaction_id>")

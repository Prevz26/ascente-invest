import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, Api
from utils.response import custom_response
from utils.exceptions import NotFoundError, ServerError, BadRequest
from .service import investment_service
from utils.decorators import user_only
from .schema import InvestmentSchema, AllInvestmentSchema, InvestmentProfit
from utils.log import get_log_path
# Setup Blueprint and API
investment_bp = Blueprint("investment", __name__, url_prefix="/investment")
api = Api(investment_bp)
# Setup logging
investment_logger = logging.getLogger(__name__)
investment_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(get_log_path('investments.log'))
file_handler.setFormatter(formatter)
investment_logger.addHandler(file_handler)


class FetchInvestment(Resource):
    @jwt_required()
    def get(self, investment_id):
        investment_logger.info(f"FetchInvestment: Received GET request for investment_id={investment_id}")
        try:
            investment_logger.info(f"FetchInvestment: Fetching investment with id={investment_id}")
            investment = investment_service.fetch_investment(investment_id)
            investment_logger.info(f"FetchInvestment: Investment fetched: {investment}")
            validated_data = InvestmentSchema(**investment).model_dump(exclude_none=True, mode="json")
            investment_logger.info(f"FetchInvestment: Investment validated data: {validated_data}")
            return custom_response.success_response(
                message="Investment fetched successfully",
                data=validated_data
            )
        except NotFoundError as e:
            investment_logger.error(f"Investment not found: {str(e)}")
            return custom_response.not_found_error()
        except ServerError as e:
            investment_logger.error(f"Error fetching investment: {str(e)}")
            return custom_response.error_response(message=str(e), status_code=500)


class FetchAllInvestments(Resource):
    @jwt_required()
    def get(self):
        investment_logger.info("FetchAllInvestments: Received GET request for all investments")
        try:
            investment_logger.info("FetchAllInvestments: Fetching all investments")
            investments = investment_service.fetch_all_investments()
            investment_logger.info(f"FetchAllInvestments: Investments fetched: {investments}")
            validated_data = AllInvestmentSchema(data = investments).model_dump(mode="json")
            investment_logger.info(f"FetchAllInvestments: Validated data: {validated_data}")
            investment_logger.info(investments)
            return custom_response.success_response(
                message="All investments fetched successfully",
                data=validated_data
            )
        except ServerError as e:
            investment_logger.error(f"Error fetching investments: {str(e)}")
            return custom_response.error_response(message=str(e), status_code=500)


class CalculateReturns(Resource):
    @jwt_required()
    def get(self, investment_id):
        investment_logger.info(f"CalculateReturns: Received GET request for investment_id={investment_id}")
        try:
            investment_logger.info(f"CalculateReturns: Calculating returns for investment_id={investment_id}")
            returns = investment_service.calculate_returns(investment_id)
            investment_logger.info(f"CalculateReturns: Returns calculated: {returns}")
            return custom_response.success_response(
                message="Returns calculated successfully",
                data=returns
            )
        except NotFoundError as e:
            investment_logger.error(f"Investment not found: {str(e)}")
            return custom_response.not_found_error()


class CheckMaturity(Resource):
    @jwt_required()
    def get(self, investment_id):
        investment_logger.info(f"CheckMaturity: Received GET request for investment_id={investment_id}")
        try:
            investment_logger.info(f"CheckMaturity: Checking maturity for investment_id={investment_id}")
            maturity = investment_service.check_maturity(investment_id)
            investment_logger.info(f"CheckMaturity: Maturity status: {maturity}")
            return custom_response.success_response(
                message="Maturity status fetched successfully",
                data=maturity
            )
        except NotFoundError as e:
            investment_logger.error(f"Investment not found: {str(e)}")
            return custom_response.not_found_error()


class CalculateDailyAmount(Resource):
    @jwt_required()
    def get(self, investment_id):
        investment_logger.info(f"CalculateDailyAmount: Received GET request for investment_id={investment_id}")
        try:
            investment_logger.info(f"CalculateDailyAmount: Calculating daily amount for investment_id={investment_id}")
            daily_amount = investment_service.calculate_daily_amount(investment_id)
            investment_logger.info(f"CalculateDailyAmount: Daily amount calculated: {daily_amount}")
            return custom_response.success_response(
                message="Daily amount calculated successfully",
                data=daily_amount
            )
        except NotFoundError as e:
            investment_logger.error(f"Investment not found: {str(e)}")
            return custom_response.not_found_error()
        except ServerError as e:
            investment_logger.error(f"Error calculating daily amount: {str(e)}")
            return custom_response.error_response(message=str(e), status_code=500)

class InvestmentProfit(Resource):
    @jwt_required()
    def get(self, investment_id):
        investment_logger.info(f"InvestmentProfit: Received GET request for investment_id={investment_id}")
        try:
            investment_logger.info(f"InvestmentProfit: Getting all profits for investment_id={investment_id}")
            profit = investment_service.get_all_profits(investment_id)
            investment_logger.info(f"InvestmentProfit: Profit data: {profit}")
            validated_data = InvestmentProfit(**profit).model_dump(exclude_none=True, mode="json")
            investment_logger.info(f"InvestmentProfit: Validated profit data: {validated_data}")
            return custom_response.success_response(
                message="Investment profit calculated successfully",
                data=validated_data
            )
        except NotFoundError as e:
            investment_logger.error(f"Investment not found: {str(e)}")
            return custom_response.not_found_error()
        except ServerError as e:
            investment_logger.error(f"Error calculating investment profit: {str(e)}")
            return custom_response.error_response(message=str(e), status_code=500)


class Withdraw(Resource):
    @jwt_required()
    @user_only()
    def post(self):
        amount = request.json.get("amount")
        investment_logger.info(f"Withdraw: Received POST request for amount={amount}")
        try:
            investment_logger.info(f"Withdraw: Processing withdrawal for investment_id={amount}")
            withdrawal = investment_service.withdraw(amount)
            return custom_response.server_error()
        except NotFoundError as e:
            investment_logger.error(f"Investment not found: {str(e)}")
            return custom_response.not_found_error()
        except ServerError as e:
            investment_logger.error(f"Error processing withdrawal: {str(e)}")
            return custom_response.error_response(message=str(e), status_code=500)
# Add route
api.add_resource(FetchInvestment, "/<int:investment_id>")
api.add_resource(FetchAllInvestments, "/all")
api.add_resource(CalculateReturns, "/<int:investment_id>/returns")
api.add_resource(CheckMaturity, "/<int:investment_id>/maturity")
api.add_resource(CalculateDailyAmount, "/<int:investment_id>/daily-amount")
api.add_resource(InvestmentProfit, "/<int:investment_id>/profit")
api.add_resource(Withdraw, "/withdraw")
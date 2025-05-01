from datetime import timedelta
from decimal import Decimal
import logging
from sqlalchemy.exc import SQLAlchemyError
from utils.dependency import db
from utils.exceptions import NotFoundError, ServerError
from utils.log import get_log_path
from .models import Investments
from v1.auth.service import auth_service
import sqlalchemy as sa 

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(get_log_path('investments.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class InvestmentService:
    def __init__(self):
        logger.info("Initializing InvestmentService")
        self.db = db.session
        self.model = Investments
        self.auth = auth_service

    def create_investment(self, amount, plan_id, wallet_id, user_id):
        """Create a new investment after payment confirmation."""
        logger.info(f"Creating investment for user {user_id} with plan {plan_id} and wallet {wallet_id}")
        try:
            logger.debug(f"Instantiating investment model with amount={amount}, user_id={user_id}, plan_id={plan_id}, wallet_id={wallet_id}")
            investment = self.model(
                amount=amount,
                user_id=user_id,
                plan_id=plan_id,
                wallet_id=wallet_id,
                invested_date=sa.func.now()
            )
            self.db.add(investment)
            logger.debug("Added investment to session")
            self.db.commit()
            logger.info(f"Successfully created investment {investment.id}")
            return investment.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"Error creating investment: {str(e)}")
            self.db.rollback()
            logger.info("Rolled back transaction due to error in create_investment")
            raise ServerError("An error occurred while creating the investment")

    def fetch_investment(self, investment_id, user_id=None):
        logger.info(f"Fetching investment with ID {investment_id}")
        if not user_id:
            logger.debug("No user_id provided, fetching from auth service")
            user_id = self.auth.get_current_user().id
        investment = self.db.query(self.model).filter_by(id=investment_id, user_id=user_id).first()
        if not investment:
            logger.warning(f"Investment with ID {investment_id} not found")
            raise NotFoundError("Investment not found")
        logger.info(f"Found investment {investment_id} for user {user_id}")
        return investment.to_dict()

    def fetch_all_investments(self, user_id=None):
        """Fetch all investments for the current user."""
        if not user_id:
            logger.debug("No user_id provided, fetching from auth service")
            user_id = self.auth.get_current_user().id
        logger.info(f"Fetching all investments for user {user_id}")
        investments = self.db.query(self.model).filter_by(user_id=user_id).all()
        logger.info(f"Found {len(investments)} investments for user {user_id}")
        for investment in investments:
            logger.info(f"Fetched investment: {investment.to_dict()}")
        return [investment.to_dict() for investment in investments]

    def calculate_returns(self, investment_id):
        """Calculate profit and total payout for an investment."""
        logger.info(f"Calculating returns for investment {investment_id}")
        investment = self.db.query(self.model).filter_by(id=investment_id).first()
        if not investment:
            logger.warning(f"Investment with ID {investment_id} not found")
            raise NotFoundError("Investment not found")
        logger.info(f"Returns for investment {investment_id}: profit={investment.profit}, total_payout={investment.total_payout}")
        return {
            "profit": investment.profit,
            "total_payout": investment.total_payout
        }

    def check_maturity(self, investment_id):
        """Check if an investment has matured."""
        logger.info(f"Checking maturity for investment {investment_id}")
        investment = self.db.query(self.model).filter_by(id=investment_id).first()
        if not investment:
            logger.warning(f"Investment with ID {investment_id} not found")
            raise NotFoundError("Investment not found")
        maturity_date = investment.maturity_date
        if not maturity_date:
            logger.error(f"Maturity date could not be calculated for investment {investment_id}")
            raise ServerError("Maturity date could not be calculated")
        logger.info(f"Investment {investment_id} maturity date: {maturity_date}, is_matured: {investment.is_matured}")
        return {
            "maturity_date": maturity_date,
            "is_matured": investment.is_matured
        }

    # def update_investment(self, investment_id, **kwargs):
    #     """Update an investment."""
    #     logger.info(f"Updating investment with ID {investment_id}")
    #     investment = self.db.query(self.model).filter_by(id=investment_id).first()
    #     if not investment:
    #         logger.warning(f"Investment with ID {investment_id} not found")
    #         raise NotFoundError("Investment not found")
    #     try:
    #         for key, value in kwargs.items():
    #             if hasattr(investment, key):
    #                 setattr(investment, key, value)
    #         self.db.commit()
    #         logger.info(f"Successfully updated investment {investment_id}")
    #         return investment.to_dict()
    #     except SQLAlchemyError as e:
    #         logger.error(f"Error updating investment: {str(e)}")
    #         self.db.rollback()
    #         raise ServerError("An error occurred while updating the investment")

    # def delete_investment(self, investment_id):
    #     """Delete an investment."""
    #     logger.info(f"Deleting investment with ID {investment_id}")
    #     investment = self.db.query(self.model).filter_by(id=investment_id).first()
    #     if not investment:
    #         logger.warning(f"Investment with ID {investment_id} not found")
    #         raise NotFoundError("Investment not found")
    #     try:
    #         self.db.delete(investment)
    #         self.db.commit()
    #         logger.info(f"Successfully deleted investment {investment_id}")
    #         return True
    #     except SQLAlchemyError as e:
    #         logger.error(f"Error deleting investment: {str(e)}")
    #         self.db.rollback()
    #         raise ServerError("An error occurred while deleting the investment")

    def calculate_daily_amount(self, investment_id):
        """Calculate the daily return amount for an investment."""
        logger.info(f"Calculating daily amount for investment {investment_id}")
        try:
            investment = self.db.query(self.model).filter_by(id=investment_id).first()
            if not investment:
                logger.warning(f"Investment with ID {investment_id} not found")
                raise NotFoundError("Investment not found")

            logger.debug(f"Calculating total_profit and maturity_date for investment {investment_id}")
            total_profit = investment.profit
            maturity_date = investment.maturity_date.get("date")
            duration_days = (maturity_date - investment.invested_date)
            logger.debug(f"Duration days for investment {investment_id}: {duration_days}")
            if duration_days <= timedelta(days=0):
                logger.error(f"Invalid investment duration for investment {investment_id}")
                raise ServerError("Invalid investment duration")

            daily_amount = total_profit / Decimal(duration_days.total_seconds() / 86400)
            logger.info(f"Daily amount for investment {investment_id}: {daily_amount}")

            return {
                "daily_amount": round(daily_amount, 2),
                "days_remaining": duration_days
            }
        except SQLAlchemyError as e:
            logger.error(f"Error calculating daily amount: {str(e)}")
            raise ServerError("An error occurred while calculating daily amount")
        

    def withdraw(self, investment_id, amount):
        """Withdraw funds from an investment if matured and sufficient balance."""
        logger.info(f"Attempting withdrawal from investment {investment_id} for amount {amount}")
        user_id = self.auth.get_current_user().id
        investment = self.db.query(self.model).filter_by(id=investment_id, user_id=user_id).first()
        if not investment:
            logger.warning(f"Investment with ID {investment_id} not found")
            raise NotFoundError("Investment not found")
        if not investment.is_matured:
            logger.warning(f"Investment {investment_id} has not matured")
            raise ServerError("Investment has not matured yet")
        if amount > investment.total_payout:
            logger.warning(f"Insufficient funds in investment {investment_id} for withdrawal")
            raise ServerError("Insufficient funds for withdrawal")
        try:
            logger.debug(f"Subtracting {amount} from investment {investment_id} total_payout")
            investment.total_payout -= amount
            self.db.commit()
            logger.info(f"Withdrawal of {amount} from investment {investment_id} successful")
            return {
                "withdrawn": amount,
                "remaining_balance": investment.total_payout
            }
        except SQLAlchemyError as e:
            logger.error(f"Error during withdrawal: {str(e)}")
            self.db.rollback()
            logger.info("Rolled back transaction due to error in withdraw")
            raise ServerError("An error occurred during withdrawal")

    def get_all_profits(self, investment_id):
        """Get all profit details for a specific investment."""
        logger.info(f"Fetching all profit details for investment {investment_id}")
        try:
            user_id = self.auth.get_current_user().id
            logger.debug(f"Fetching investment for user {user_id}")
            investment = self.db.query(self.model).filter_by(id=investment_id, user_id=user_id).first()
            if not investment:
                logger.warning(f"Investment with ID {investment_id} not found for user {user_id}")
                raise NotFoundError("Investment not found")
            logger.info(f"Profit details for investment {investment_id} fetched successfully")
            return {
                "investment_id": investment.id,
                "user_id": investment.user_id,
                "plan_id": investment.plan_id,
                "amount_invested": float(investment.amount),
                "invested_date": investment.invested_date,
                "maturity_date": investment.maturity_date,
                "is_matured": investment.is_matured,
                "profit": float(investment.profit),
                "total_payout": float(investment.total_payout),
                "status": investment.status,
                "wallet_id": investment.wallet_id
            }
        except SQLAlchemyError as e:
            logger.error(f"Error fetching profit details: {str(e)}")
            raise ServerError("An error occurred while fetching profit details")
        
investment_service = InvestmentService()
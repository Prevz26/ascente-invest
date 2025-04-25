# import parsedatetime
# import datetime


# cal = parsedatetime.Calendar()
# date_string = "dd"
# # Parse a human-readable time string
# time_struct, parse_status = cal.parse(date_string)
# # Convert to just date
# parsed_date = datetime.date(*time_struct[:3])
# # plan_details["duration"] = parsed_date


# def calculate_roi(plans):
#     time_units = {"days": 365, "weeks": 52, "months": 12, "years": 1}  # Conversion to yearly factor
#     results = []

#     for plan in plans:
#         name, cost, roi_percent, duration, unit = plan
#         roi_decimal = roi_percent / 100

#         # Calculate total return dynamically (capital + profit)
#         total_return = cost + (cost * roi_decimal)

#         # Convert duration to years
#         if unit not in time_units:
#             raise ValueError(f"Invalid time unit: {unit}. Use 'days', 'weeks', 'months', or 'years'.")
#         duration_in_years = duration / time_units[unit]

#         # Calculate annualized ROI
#         annualized_roi = ((1 + roi_decimal) ** (1 / duration_in_years) - 1) * 100  

#         results.append({
#             "Plan": name,
#             "Capital ($)": cost,
#             "ROI (%)": roi_percent,
#             "Duration": f"{duration} {unit}",
#             "Total Return ($)": round(total_return, 2),
#             "Annualized ROI (%)": round(annualized_roi, 2)
#         })
    
#     # Sort by Annualized ROI in descending order
#     results = sorted(results, key=lambda x: x["Annualized ROI (%)"], reverse=True)

#     return results


# # Example plans: (name, cost, ROI %, duration, unit)
# plans = [
#     ("Plan A", 1000, 50, 3, "weeks"),
#     ("Plan B", 2000, 75, 1, "months"),
#     ("Plan C", 5000, 140, 6, "months"),
#     ("Plan D", 7000, 185.71, 2, "years"),
# ]

# # Run the function
# roi_results = calculate_roi(plans)

# # Print the results
# for res in roi_results:
#     print(res)



#this service handles when the user has bougtht a plan


import logging
from sqlalchemy.exc import SQLAlchemyError
from utils.dependency import db
from utils.exceptions import NotFoundError, ServerError
from .models import Investments
from v1.auth.service import auth_service
import sqlalchemy as sa 

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/investments.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class InvestmentService:
    def __init__(self):
        self.db = db.session
        self.model = Investments
        # self.auth = auth_service

    def create_investment(self, amount, plan_id, wallet_id, user_id):
        """Create a new investment after payment confirmation."""
        logger.info(f"Creating investment for user {user_id} with plan {plan_id} and wallet {wallet_id}")
        try:
            investment = self.model(
                amount=amount,
                user_id=user_id,
                plan_id=plan_id,
                wallet_id=wallet_id,
                invested_date=sa.func.now()
            )
            self.db.add(investment)
            self.db.commit()
            logger.info(f"Successfully created investment {investment.id}")
            return investment.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"Error creating investment: {str(e)}")
            self.db.rollback()
            raise ServerError("An error occurred while creating the investment")

    def fetch_investment(self, investment_id, user_id):
        """Fetch details of a specific investment."""
        logger.info(f"Fetching investment with ID {investment_id}")
        investment = self.db.query(self.model).filter_by(id=investment_id, user_id=user_id).first()
        if not investment:
            logger.warning(f"Investment with ID {investment_id} not found")
            raise NotFoundError("Investment not found")
        return investment.to_dict()

    def fetch_all_investments(self, user_id):
        """Fetch all investments for the current user."""
        logger.info(f"Fetching all investments for user {user_id}")
        investments = self.db.query(self.model).filter_by(user_id=user_id).all()
        return [investment.to_dict() for investment in investments]

    def calculate_returns(self, investment_id):
        """Calculate profit and total payout for an investment."""
        investment = self.db.query(self.model).filter_by(id=investment_id).first()
        if not investment:
            logger.warning(f"Investment with ID {investment_id} not found")
            raise NotFoundError("Investment not found")
        return {
            "profit": investment.profit,
            "total_payout": investment.total_payout
        }

    def check_maturity(self, investment_id):
        """Check if an investment has matured."""
        investment = self.db.query(self.model).filter_by(id=investment_id).first()
        if not investment:
            logger.warning(f"Investment with ID {investment_id} not found")
            raise NotFoundError("Investment not found")
        maturity_date = investment.maturity_date
        if not maturity_date:
            raise ServerError("Maturity date could not be calculated")
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

            total_profit = investment.profit
            maturity_date = investment.maturity_date.get("date")
            duration_days = (maturity_date - investment.invested_date)
            if duration_days <= 0:
                raise ServerError("Invalid investment duration")

            daily_amount = total_profit / duration_days
            return {
                "daily_amount": round(daily_amount, 2),
                "days_remaining": duration_days
            }
        except SQLAlchemyError as e:
            logger.error(f"Error calculating daily amount: {str(e)}")
            raise ServerError("An error occurred while calculating daily amount")

investment_service = InvestmentService()
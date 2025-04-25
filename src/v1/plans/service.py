import datetime
import logging
from utils.dependency import db
from urllib.parse import urlencode
from utils.exceptions import NotActive, NotFoundError, ServerError
from sqlalchemy.exc import SQLAlchemyError
from .models import Plan, Wallet, Transaction
from .schema import PendingCallback, RequestCryptApiSchema, ResponseCryptApiSchema, LogResponseSchema, CallBack, SuccessCallback
from v1.auth.service import auth_service
import requests
from v1.investments.service import investment_service
from v1.investments.models import Investments
import uuid

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/plans.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



class CryptApi():
    def __init__(self, ticker:str):
        self.ticker = ticker
        self.url = f"https://api.cryptapi.io/{self.ticker}/create/"

    def create_address(self, **kwargs):
        logger.info(f"Creating crypto address for ticker: {self.ticker}")
        logger.debug(f"Address parameters: {kwargs}")
        address_params = RequestCryptApiSchema(**kwargs).model_dump(by_alias=True)
        try:
            response = requests.get(self.url, params=address_params)
            logger.info(f"Successfully created address for {self.ticker}")
            validated_response = ResponseCryptApiSchema(**response.json()).model_dump()
            logger.debug(f"Response data: {validated_response}")
            return validated_response
        except requests.RequestException as e:
            logger.error(f"Error creating address for {self.ticker}: {str(e)}")
            raise ServerError("Failed to create crypto address")

    def check_log(self, callback:str):
        logger.info(f"Checking logs for ticker: {self.ticker}")
        logger.debug(f"Callback URL: {callback}")
        url = self.url.replace('create', 'logs')
        validated_callback = CallBack(callback=callback).model_dump()
        try:
            response = requests.get(url, params=validated_callback)
            logger.info(f"Successfully retrieved logs for {self.ticker}")
            validated_response = LogResponseSchema(**response.json()).model_dump()
            logger.debug(f"Log response data: {validated_response}")
            return validated_response
        except requests.RequestException as e:
            logger.error(f"Error retrieving logs for {self.ticker}: {str(e)}")
            raise ServerError("Failed to create crypto address")
        
    def convert(self, ticker, value, from_currency):
        logger.info(f"Converting {value} {from_currency} to {ticker}")
        url = f"https://api.cryptapi.io/{ticker}/convert/"
        query = {
            "value": value,
            "from": from_currency,
        }
        try:
            response = requests.get(url, params=query)
            response.raise_for_status()  # Raises HTTPError for bad responses
            logger.info(f"Successfully converted {value} {from_currency} to {ticker}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error converting currency: {str(e)}")
            raise ServerError("Failed to convert currency")

class UserPlanService:
    def __init__(self):
        self.db = db.session
        self.model = Plan
        self.user = auth_service
        self.base_callback = "https://webhook.site/97f0d5cc-d809-46dc-9a16-1bd1c2f09d9c"

        self.address = {
                'trc20/usdt': 'TSgcQFPgLy9wZH2HTp6Co59rXE4HG1cv4n',
                'eth': '0x1020103496a517c74B3Db4311D6FB242715b2bc4',
                'btc': 'bc1qkk3ur773wu4maen4ntjpkqhzlkphfsjh82c4qd',
                'trx': 'TSgcQFPgLy9wZH2HTp6Co59rXE4HG1cv4n',
            }
        self.me_address = {
                'trc20/usdt': 'TF7J6iEo85oow4bRtNsgqXYjfzeNdF6DG8',
                'eth': '0x71e4439dd751668d03ec45bc63cff51efdc3441e',
                'btc': 'bc1qmgtmfqj4edpd4wu0e3awukuaaaj5au445l0a6d',
                'trx': 'TF7J6iEo85oow4bRtNsgqXYjfzeNdF6DG8',
        }
    
    def _generate_transaction_id(self):
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4().hex)[:8]
        return f"{current_time}-{unique_id}"
    
    def get_all_plans(self):
        logger.info("Fetching all plans")
        try:
            plans = self.db.query(self.model).all()
            return [plan.to_dict() for plan in plans]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching plans: {str(e)}")
            raise ServerError("An error occurred while fetching plans")

    def get_single_plan(self, plan_id):
        logger.info(f"Fetching plan with id: {plan_id}")
        plan = self.db.query(self.model).filter_by(id=plan_id).first()
        if not plan:
            logger.warning(f"Plan with id {plan_id} not found")
            raise NotFoundError("Plan not found")
        return plan.to_dict()

    def handle_callback(self, transaction_id, **data):
        logger.info("Received callback for wallet transaction")
        try:
            # Find associated transaction
            transaction = self.db.query(Transaction).filter_by(transaction_id=transaction_id, status="pending", transaction_type="buy plan").first()
            if not transaction:
                logger.error("Transaction not found for callback")
                raise NotFoundError("Transaction not found")

            # Validate and process based on confirmation status
            if data.get('confirmations', 0) == 1:
                validated_data = SuccessCallback(**data).model_dump()
            elif data.get('confirmations', 0) == 0:
                validated_data = PendingCallback(**data).model_dump()
            else:
                validated_data = SuccessCallback(**data).model_dump()

            confirmations = validated_data.get('confirmations', 0)
            investment = None

            if confirmations == 1:
                # Complete transaction
                transaction.status = 'completed'
                transaction.blockchain_in = validated_data.get('address_in')
                transaction.blockchain_out = validated_data.get('address_out')
                transaction.crytp_api_uuid = validated_data.get('uuid')
                
                # Create active investment
                investment = Investments(
                    amount=validated_data["value_forwarded_coin_convert"]["USD"],
                    user_id=transaction.user_id,
                    plan_id=transaction.plan_id,
                    status="active",
                    is_active=True,
                    invested_date=datetime.datetime.now()
                )
                self.db.add(investment)

            elif confirmations == 0:
                # Keep transaction pending
                transaction.status = 'pending'
                transaction.blockchain_in = validated_data.get('address_in')
                transaction.crytp_api_uuid = validated_data.get('uuid')

            elif validated_data.get('status') == 'failed':
                # Mark as failed
                transaction.status = 'failed'

            self.db.commit()
            if investment:
                logger.info(f"Successfully processed callback for investment {investment.id}")
            else:
                logger.info(f"Successfully processed callback for transaction {transaction_id}")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error processing callback: {str(e)}")
            self.db.rollback()
            raise ServerError("Error processing callback")
        
        
    def buy_plan_directly(self, plan_id, token, amount):
        user_id = self.user.get_current_user().id
        logger.info(f"Processing direct plan purchase for user {user_id}, plan {plan_id}")
        logger.debug(f"Purchase details - Token: {token}, Amount: {amount}")
        
        try:
            # Get plan details
            plan = self.db.query(Plan).filter_by(id=plan_id).first()
            if not plan:
                logger.error(f"Plan {plan_id} not found")
                raise NotFoundError("Plan not found")

            logger.debug(f"Plan details - Minimum: {plan.minimum}, Maximum: {plan.maximum}")

            if int(amount) < plan.minimum:
                logger.error(f"Amount {amount} is less than minimum required {plan.minimum}")
                raise ServerError(f"Amount must be at least {plan.minimum}")

            if int (amount) > plan.maximum:
                logger.error(f"Amount {amount} exceeds maximum allowed {plan.maximum}")
                raise ServerError(f"Amount cannot exceed {plan.maximum}")

            # Initialize crypto payment
            logger.debug(f"Initializing crypto payment with token: {token}")
            crypt = CryptApi(ticker=token)
            address = f"0.3@{self.me_address[token]}|0.7@{self.address[token]}"
            logger.debug(f"Split payment address configured: {address}")
            
            transaction_id = self._generate_transaction_id()
            logger.debug(f"Generated transaction ID: {transaction_id}")
            
            params = {
                "transaction_id": transaction_id,
            }
            query_string = urlencode(params)
            self.callback = f"{self.base_callback}?{query_string}"
            logger.debug(f"Callback URL created: {self.callback}")
            
            info = {
                "callback": self.callback,
                "address": address,
                "post": 1,
                "json": 1
            }
            
            convert = crypt.convert(ticker=token, value=amount, from_currency="USD")
            logger.info(f"conversion: {convert}")
            logger.debug(f"Requesting payment address with params: {info}")
            data = crypt.create_address(**info)
            payment_address = data["address_in"]
            logger.info(f"Payment address generated: {payment_address}")
            
            # Create transaction record
            logger.debug("Creating transaction record")
            transaction = Transaction(
                user_id=user_id,
                token=token,
                plan_id = plan.id,
                previous_balance = 0,
                present_balance = amount,
                status='pending',
                transaction_id=transaction_id,
                transaction_type = "buy plan"
            )            
            
            self.db.add(transaction)
            self.db.commit()
            logger.info(f"Transaction record created with ID: {transaction_id}")
            
            return {
                "payment_address": payment_address,
                "amount": convert["value_coin"],
                "exchange_rate": convert["exchange_rate"],
                "token": token
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error during direct plan purchase: {str(e)}")
            self.db.rollback()
            raise ServerError("An error occurred while processing the purchase")
        
    

        
        
    # def buy_plan_through_wallet(self, plan_id):
    #     user_id = self.user.get_current_user().id
    #     logger.info(f"Processing wallet plan purchase for user {user_id}, plan {plan_id}")
    #     try:
    #         # Get wallet and plan
    #         wallet = self.db.query(self.model).filter_by(user_id=user_id).first()
    #         plan = self.db.query(Plan).filter_by(id=plan_id).first()

    #         if not wallet:
    #             logger.error(f"Wallet not found for user {user_id}")
    #             raise NotFoundError("Wallet not found")
            
    #         if not plan:
    #             logger.error(f"Plan {plan_id} not found")
    #             raise NotFoundError("Plan not found")

    #         # Check if wallet has sufficient balance
    #         if wallet.balance < plan.minimum:
    #             logger.error(f"Insufficient balance in wallet {wallet.id}")
    #             raise ServerError("Insufficient balance in wallet")

    #         # Create transaction record
    #         transaction = Transaction(
    #             user=wallet.user,
    #             wallet=wallet,
    #             token="WALLET",
    #             previous_balance=wallet.balance,
    #             present_balance=wallet.balance - plan.minimum,
    #             status='completed'
    #         )
    #         investment = investment_service
    #         investment.create_investment(
    #             amount=plan.minimum,
    #             plan_id=plan_id,
    #             wallet_id=wallet.id
    #         )

    #         # Update wallet balance
    #         wallet.balance -= plan.price
            
    #         self.db.add(transaction)
    #         self.db.commit()
            
    #         logger.info(f"Successfully purchased plan {plan_id} through wallet")
    #         return transaction.to_dict()

    #     except SQLAlchemyError as e:
    #         logger.error(f"Database error during plan purchase: {str(e)}")
    #         self.db.rollback()
    #         raise ServerError("An error occurred while processing the purchase")





class WalletService:
    def __init__(self):
        self.db = db.session
        self.model = Wallet
        self.auth = auth_service

    def _create_wallet(self, balance=0):
        user_id = self.auth.get_current_user().id
        logger.info(f"Creating wallet for user {user_id}")
        existing_wallet = self.db.query(self.model).filter_by(user_id=user_id).first()
        if existing_wallet:
            logger.info(f"User {user_id} already has a wallet, returning existing wallet")
            return existing_wallet

        try:
            wallet = self.model(user_id=user_id, balance=balance)
            self.db.add(wallet)
            self.db.commit()
            logger.info(f"Successfully created new wallet for user {user_id} with balance {balance}")
            return wallet
        except SQLAlchemyError as e:
            logger.error(f"Error creating wallet for user {user_id}: {str(e)}")
            self.db.rollback()
            raise ServerError("An error occurred while creating wallet")


    def fund_wallet_with_daily_profit(self, investment_id):
        user_id = self.auth.get_current_user().id
        logger.info(f"Processing daily profit for investment {investment_id}")
        try:
            # Get the investment and check if it's active
            investment = investment_service.fetch_investment(investment_id, user_id)
            if not investment or not investment.get('is_active'):
                logger.warning(f"Investment {investment_id} not found or not active")
                raise NotActive("Investment Not active")

            # Check if 24 hours have passed since last profit
            current_time = datetime.datetime.now()
            investment_record = self.db.query(Investments).filter_by(id=investment_id, user_id=user_id).first()
            last_profit_time = investment_record.profit_added or investment_record.created_at
            time_diff = current_time - last_profit_time
            
            if time_diff.total_seconds() < 86400:  # 86400 seconds = 24 hours
                logger.info(f"24 hours haven't passed since last profit for investment {investment_id}")
                return False

            # Calculate and add daily profit
            daily_profit = investment_service.calculate_daily_amount(investment_id)["daily_amount"]
            if daily_profit:
                wallet = self.db.query(self.model).filter_by(user_id=user_id).first()
                if not wallet:
                    logger.warning(f"No wallet found for user {investment['user_id']}")
                    wallet = self._create_wallet()
                
                wallet.balance += daily_profit
                # Update last profit time
                investment_service.update_last_profit_time(investment_id, current_time)
                self.db.commit()
                logger.info(f"Successfully added daily profit {daily_profit} to wallet")
                return True

            
        except SQLAlchemyError as e:
            logger.error(f"Database error while funding wallet: {str(e)}")
            self.db.rollback()
            raise ServerError("Error processing daily profit")


    def check_balance(self):
        user_id = self.auth.get_current_user().id
        logger.info(f"Checking wallet balance for user {user_id}")
        wallet = self.db.query(self.model).filter_by(user_id=user_id).first()
        if not wallet:
            logger.info(f"No wallet found for user {user_id}, creating new wallet")
            check_wallet = self._create_wallet()
            logger.info(f"Returning balance {check_wallet.balance} for newly created wallet")
            return check_wallet.balance
        logger.info(f"Returning balance {wallet.balance} for existing wallet")
        return wallet.balance



wallet_service = WalletService()
user_plan_service = UserPlanService()
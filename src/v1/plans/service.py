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
from sqlalchemy import and_ 
from v1.plans.models import TransactionStatus
from utils.log import get_log_path

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(get_log_path('plans.log'))
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
            # Early validation of transaction existence
            if not transaction_id:
                logger.error("No transaction ID provided")
                raise NotFoundError("Transaction ID is required")

            # Find associated transaction
            transaction = self.db.query(Transaction).filter(
                and_(
                    Transaction.transaction_id == transaction_id,
                    Transaction.status == TransactionStatus.pending
                )
            ).first()

            if not transaction:
                logger.error("Transaction not found or not in pending state")
                raise NotFoundError("Transaction not found or already processed")

            # Early validation of data
            if not data:
                logger.error("No callback data provided")
                raise ServerError("Invalid callback data")

            # Prepare base transaction updates
            transaction.blockchain_in = data.get('address_in')
            transaction.crytp_api_uuid = data.get('uuid')

            # Handle failed status first
            if data.get('status') == 'failed':
                transaction.status = 'failed'
                self.db.add(transaction)
                self.db.commit()
                logger.info(f"Transaction {transaction_id} marked as failed")
                return True

            # Validate callback data format
            try:
                if data.get('confirmations', 0) == 1:
                    validated_data = SuccessCallback(**data).model_dump()
                elif data.get('confirmations', 0) == 0:
                    validated_data = PendingCallback(**data).model_dump()
                else:
                    validated_data = SuccessCallback(**data).model_dump()
            except Exception as e:
                logger.error(f"Invalid callback data format: {str(e)}")
                raise ServerError("Invalid callback data format")

            # Determine status and prepare investment if needed
            investment = None
            if validated_data.get('confirmations', 0) == 0:
                transaction.status = TransactionStatus.pending
            else:
                transaction.status = TransactionStatus.success
                transaction.amount = validated_data.get('value_forwarded_coin_convert')["USD"]
                transaction.blockchain_out = validated_data.get('address_out')
                investment = Investments(
                    amount=validated_data["value_forwarded_coin_convert"]["USD"],
                    user_id=transaction.user_id,
                    plan_id=transaction.plan_id,
                    status="active",
                    is_active=True,
                    invested_date=datetime.datetime.now()
                )

            # Perform all database updates
            self.db.add(transaction)
            if investment:
                self.db.add(investment)
            self.db.commit()
            
            logger.info(f"Transaction {transaction_id} processed with status: {transaction.status}")
            return True


        except SQLAlchemyError as e:
            logger.error(f"Database error processing callback: {str(e)}")
            self.db.rollback()
            raise ServerError("Error processing callback")
    
    def check_payment_status(self, transaction_id):
        user_id = self.user.get_current_user().id
        logger.info(f"Checking payment status for user {user_id}, transaction {transaction_id}")
    
        try:
            transaction = self.db.query(Transaction).filter_by(transaction_id=transaction_id, user_id=user_id).first()
            if not transaction:
                logger.error(f"Transaction {transaction_id} not found")
                raise NotFoundError("Transaction not found")
            # logger.info(f"Transaction status: {transaction.status}")
            transaction_data = transaction.to_dict()
            # logger.info(f"Transaction data: {transaction_data}")
            data =  {
                "status": transaction_data.get("status"),
                "transaction_id": transaction_data.get("transaction_id"),
                "transaction_type": transaction_data.get("transaction_type"),
                "token": transaction_data.get("token"),
            }
            logger.info(f"Data to be sent: {data}")
            return data
        
        except SQLAlchemyError as e:
            logger.error(f"Database error checking payment status: {str(e)}")
            raise ServerError("Error checking payment status")
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}")
            raise ServerError("Failed to check payment status")

        
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
                status=TransactionStatus.pending,
                transaction_id=transaction_id,
                transaction_type = "buy plan"
            )            
            
            self.db.add(transaction)
            self.db.commit()
            logger.info(f"Transaction record created with ID: {transaction_id}")
            
            return {
                "plan_id": plan.id,
                "plan_name": plan.name,
                "transaction_id": transaction_id,
                "payment_address": payment_address,
                "amount": float(convert["value_coin"]),
                "exchange_rate": float(convert["exchange_rate"]),
                "total": float(convert["value_coin"]) + float(convert["exchange_rate"]),
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


    def fund_wallet_with_daily_profit(self, user_id):
        # user_id = self.auth.get_current_user().id   
        logger.info(f"Processing daily profit for all active investments for user {user_id}")
        try:
            # Fetch all active investments for the user
            investments = investment_service.fetch_all_investments()
            if not investments:
                logger.info(f"No active investments found for user {user_id}")
                return False

            updated = False
            for investment in investments:
                if not investment.get('is_active'):
                    logger.info(f"Skipping inactive investment {investment.get('id')}")
                    continue

                investment_id = investment.get('id')
                investment_record = self.db.query(Investments).filter_by(id=investment_id, user_id=user_id).first()
                if not investment_record:
                    logger.warning(f"Investment record {investment_id} not found in DB")
                    continue

                current_time = datetime.datetime.now(datetime.timezone.utc)
                last_profit_time = investment_record.date_profit_added or investment_record.created_at
                if last_profit_time.tzinfo is None:
                    last_profit_time = last_profit_time.replace(tzinfo=datetime.timezone.utc)
                logger.info(
                    f"\ncurrent_time: {current_time} tzinfo: {current_time.tzinfo}\n"
                    f"last_profit_time: {last_profit_time} tzinfo: {last_profit_time.tzinfo}\n"
                )
                time_diff = current_time - last_profit_time

                if time_diff.total_seconds() < 86400:  # 24 hours
                    logger.info(f"24 hours haven't passed since last profit for investment {investment_id}")
                    continue

                daily_profit = investment_service.calculate_daily_amount(investment_id)["daily_amount"]
                if daily_profit:
                    wallet = self.db.query(self.model).filter_by(user_id=user_id).first()
                    if not wallet:
                        logger.warning(f"No wallet found for user {user_id}")
                        wallet = self._create_wallet()

                    wallet.balance += daily_profit

                    transaction = Transaction(
                        user_id=user_id,
                        wallet_id=wallet.id,
                        plan_id=investment_record.plan_id,
                        transaction_type="daily profit",
                        token="USD",
                        previous_balance=wallet.balance - daily_profit,
                        present_balance=wallet.balance,
                        status=TransactionStatus.success,
                    )
                    self.db.add(transaction)

                    investment_record.profit_added = daily_profit
                    investment_record.last_viewed = current_time
                    investment_record.wallet_id = wallet.id
                    investment_record.date_profit_added = current_time
                    self.db.add(investment_record)

                    updated = True
                    logger.info(f"Added daily profit {daily_profit} to wallet for investment {investment_id}")

            if updated:
                self.db.commit()
                logger.info("Successfully added daily profits for eligible investments")
                return True
            else:
                logger.info("No eligible investments for daily profit update")
                return False

        except SQLAlchemyError as e:
            logger.error(f"Database error while funding wallet: {str(e)}")
            self.db.rollback()
            raise ServerError("Error processing daily profit")

    def check_balance(self):
        user_id = self.auth.get_current_user().id
        logger.info(f"Checking wallet balance for user {user_id}")
        # Update wallet with daily profit before checking balance
        # investments = self.db.query(Investments).filter_by(user_id=user_id, is_active=True).all()
        try:
            self.fund_wallet_with_daily_profit(user_id)
        except ValueError as e:
            logger.warning(f"Could not fund wallet for user {user_id}: {str(e)}")
        wallet = self.db.query(self.model).filter_by(user_id=user_id).first()
        if not wallet:
            logger.info(f"No wallet found for user {user_id}, creating new wallet")
            check_wallet = self._create_wallet()
            logger.info(f"Returning balance {check_wallet.balance} for newly created wallet")
            return {"balance": check_wallet.balance}
        logger.info(f"Returning balance {wallet.balance} for existing wallet")
        return {"balance": wallet.balance}



wallet_service = WalletService()
user_plan_service = UserPlanService()
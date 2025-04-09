import logging
from utils.dependency import db
from utils.exceptions import NotFoundError, ServerError
from sqlalchemy.exc import SQLAlchemyError
from .models import Plan, Wallet, Transaction
from .schema import RequestCryptApiSchema, ResponseCryptApiSchema, LogResponseSchema, CallBack
from v1.auth.service import auth_service
import requests

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


class UserPlanService:
    def __init__(self):
        self.db = db.session
        self.model = Plan

    def get_all_plans(self):
        logger.info("Fetching all plans")
        try:
            plans = self.db.query(self.model).all()
            return [plan.to_dict() for plan in plans]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching plans: {str(e)}")
            raise ServerError("An error occurred while fetching plans")

    def fetch_single_plan(self, plan_id):
        logger.info(f"Fetching plan with id: {plan_id}")
        plan = self.db.query(self.model).filter_by(id=plan_id).first()
        if not plan:
            logger.warning(f"Plan with id {plan_id} not found")
            raise NotFoundError("Plan not found")
        return plan.to_dict()

    def buy_plan_directly(self, user_id, plan_id, **payment_details):
        logger.info(f"Processing direct plan purchase for user {user_id}")
        # Implement direct plan purchase logic
        pass
    
    def fetch_all_paid_plans(self):
        pass


class WalletService:
    def __init__(self):
        self.db = db.session
        self.model = Wallet
        self.auth = auth_service
        self.callback = "http://127.0.0.1:8000/investment/webhook"
        self.address = {
                'trc20/usdt': 'TSgcQFPgLy9wZH2HTp6Co59rXE4HG1cv4n',
                'eth': '0x1020103496a517c74B3Db4311D6FB242715b2bc4',
                'btc': 'bc1qkk3ur773wu4maen4ntjpkqhzlkphfsjh82c4qd',
                'trx': 'TSgcQFPgLy9wZH2HTp6Co59rXE4HG1cv4n',
            }
        self.me_address = {}

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

    def handle_callback(self, data):
        logger.info("Received callback for wallet transaction")
        crypt = CryptApi(data) #get the ticker and pass it as an argument before the data, use pydantic schema 
        crypt.check_log(callback=self.callback)
        pass # this will handle the callback info, update the transaction table and the wallet of the user 

    def fund_wallet(self, amount, token):
        user_id = self.auth.get_current_user().id
        logger.info(f"Starting wallet funding process for user {user_id} with amount {amount} {token}")
        wallet = self.db.query(self.model).filter_by(user_id=user_id).first()
        if not wallet:
            logger.info(f"No existing wallet found for user {user_id}, creating new wallet")
            self._create_wallet(balance=amount)


        try:
            logger.debug(f"Initializing CryptApi for token: {token}")
            crypt = CryptApi(ticker=token)
            info = {
                "callback": self.callback,
                "address": self.address[token],
                "post":1,
                "json":1
            }
            logger.debug(f"Requesting payment address with parameters: {info}")
            data = crypt.create_address(**info)
            logger.info(data)
            payment_address = data["address_in"]
            logger.info(f"Generated payment address: {payment_address}")

            logger.debug(f"Creating transaction record for wallet {wallet.id}")
            transaction = Transaction(
                user=wallet.user,
                wallet=wallet,
                token=token,
                previous_balance=wallet.balance,
                present_balance=wallet.balance + float(amount),
                status='pending'
            )
            self.db.add(transaction)
            self.db.commit()
            logger.info(f"Successfully created transaction record for wallet funding")
            return payment_address 
        
        except SQLAlchemyError as e:
            logger.error(f"Database error during wallet funding for user {user_id}: {str(e)}")
            self.db.rollback()
            raise ServerError("An error occurred while funding wallet")

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

    def buy_plan_through_wallet(self, wallet_id, plan_id):
        logger.info(f"Processing wallet plan purchase for wallet {wallet_id}")
        # Implement wallet plan purchase logic
        pass

class InvestmentService:
    def __init__(self):
        self.db = db.session

    def get_investment_info(self, investment_id):
        logger.info(f"Fetching investment info for {investment_id}")
        # Implement investment info logic
        pass

    def check_investment_dates(self, investment_id):
        logger.info(f"Checking investment dates for {investment_id}")
        # Implement investment dates check logic
        pass


wallet_service = WalletService()
investment_service = InvestmentService()
user_plan_service = UserPlanService()
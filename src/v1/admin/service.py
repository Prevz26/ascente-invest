import logging 
from v1.plans.models import Plan
from utils.dependency import db
from v1.auth.service import auth_service
from utils.exceptions import AlreadyExistsError, ServerError, NotFoundError
from sqlalchemy.exc import SQLAlchemyError
# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/admin.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class AdminService():
    def __init__(self):
        self.db = db.session
        self.model = Plan
        self.auth = auth_service
        

    def create_plan(self, **plan_details):
        logger.info(f"Creating new plan with details: {plan_details}")
        
        name = plan_details["name"]
        check_plan = self.db.query(self.model).filter_by(name=name).first()
        
        if check_plan:
            logger.warning(f"Plan '{name}' already exists")
            raise AlreadyExistsError("Plan already exists")
        
        try:
            new_plan = self.model(**plan_details)
            self.db.add(new_plan)
            self.db.commit()
            self.db.refresh(new_plan)
        except SQLAlchemyError as e:
            logger.error(f"Error creating plan: {str(e)}")
            self.db.rollback()
            raise ServerError("An error occurred while creating the plan")
            
        logger.info(f"Successfully created plan: {name}")
        return new_plan.to_dict()


    def update_plan(self, id, **plan_details):
        logger.info(f"Updating plan {id} with details: {plan_details}")
        
        plan = self.db.query(self.model).filter_by(id=id).first()
        if not plan:
            logger.warning(f"Plan with id {id} not found")
            raise NotFoundError("Plan not found")
        
        try:
            for key, value in plan_details.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)
            self.db.commit()
            self.db.refresh(plan)
        except SQLAlchemyError as e:
            logger.error(f"Error updating plan: {str(e)}")
            self.db.rollback()
            raise ServerError("An error occurred while updating the plan")
            
        logger.info(f"Successfully updated plan with id: {id}")
        return plan.to_dict()

    def delete_plan(self, id):
        logger.info(f"Deleting plan with id: {id}")
        
        plan = self.db.query(self.model).filter_by(id=id).first()
        if not plan:
            logger.warning(f"Plan with id {id} not found")
            raise NotFoundError("Plan not found")
        
        try:
            self.db.delete(plan)
            self.db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error deleting plan: {str(e)}")
            self.db.rollback()
            raise ServerError("An error occurred while deleting the plan")
            
        logger.info(f"Successfully deleted plan with")
        return True
    
    def fetch_all_plans(self):
        all_plans = self.db.query(self.model).all()
        logger.info([plan.to_dict() for plan in all_plans])
        return [plan.to_dict() for plan in all_plans]

    def fetch_single_plans(self, id):
        logger.info(f"Fetching plan with id: {id}")
        
        plan = self.db.query(self.model).filter_by(id=id).first()
        if not plan:
            logger.warning(f"Plan with id {id} not found")
            raise NotFoundError("Plan not found")
            
        logger.info(f"Successfully fetched plan: {plan.to_dict()}")
        return plan.to_dict()

    def view_wallet(self):
        pass 

    def fetch_all_users(self):
        pass

    def fetch_users_wallet(self):
        pass 



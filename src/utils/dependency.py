from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from .config import get_env_value
# from celery import Celery


SECRET_KEY = get_env_value("SECRET_KEY")

serializer = URLSafeTimedSerializer(SECRET_KEY)
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()
# celery = Celery() 



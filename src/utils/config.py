
from datetime import timedelta
import os
from .exceptions import Environment_Variable_Exception
from dotenv import load_dotenv, find_dotenv, set_key


def get_env_value(var_name: str) -> str | None:
    """Function to get the value of an environment variable."""
    load_dotenv(find_dotenv())
    value = os.getenv(var_name)
    if value is None:
        raise Environment_Variable_Exception(
            f"Environment variable '{var_name}' not found. Please check your .env file."
        )
    return value

class Config:
    DEBUG = get_env_value("DEBUG") == 'True'
    SECRET_KEY = get_env_value("SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=20)
    JWT_IDENTITY_CLAIM = "unique_id"

    # celery config
    CELERY = {
        "broker_url": get_env_value("CELERY_BROKER_URL"),
        "result_backend": get_env_value("CELERY_RESULT_BACKEND"),
        "timezone": "UTC",
        "task_track_started": True,
        "task_time_limit": 30 * 60
    }

    #google_config
    CLIENT_ID = get_env_value("CLIENT_ID")
    PROJECT_ID = get_env_value("PROJECT_ID")
    AUTH_URI = get_env_value("AUTH_URI")
    TOKEN_URI = get_env_value("TOKEN_URI")
    AUTH_PROVIDER_X509_CERT_URL = get_env_value("AUTH_PROVIDER_X509_CERT_URL")
    CLIENT_SECRET = get_env_value("CLIENT_SECRET")
    REDIRECT_URI = get_env_value("REDIRECT_URI")
    GOOGLE_USER_INFO = get_env_value("GOOGLE_USER_INFO")

    #smtp config

    MAIL_SERVER = get_env_value("MAIL_SERVER")
    MAIL_PORT = get_env_value("MAIL_PORT")
    MAIL_USERNAME = get_env_value("MAIL_USERNAME")
    MAIL_PASSWORD = get_env_value("MAIL_PASSWORD")
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_DEFAULT_SENDER = "nkangprecious26@gmail.com"



    
    # Set the upload folder
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_file_path(filename):
    return os.path.join(Config.UPLOAD_FOLDER, filename)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_env_value("URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = get_env_value("SQLALCHEMY_TRACK_MODIFICATIONS") == 'True'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_env_value("URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = get_env_value("SQLALCHEMY_TRACK_MODIFICATIONS") == 'True'


from celery import Celery, Task

def celery_init_app(app) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    # celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
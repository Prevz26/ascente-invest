
from celery import Celery, Task
import os
# import yaml
from typing import Dict, Any
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
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
    print(docs_dir)
    SWAGGER = {
    'title': 'My Cool Flask-RESTful API',
    'uiversion': 3,
    'doc_dir': docs_dir 
}
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
#     UPLOAD_FOLDER = 'uploads'
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def get_file_path(filename):
#     return os.path.join(Config.UPLOAD_FOLDER, filename)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_env_value("URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = get_env_value("SQLALCHEMY_TRACK_MODIFICATIONS") == 'True'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_env_value("URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = get_env_value("SQLALCHEMY_TRACK_MODIFICATIONS") == 'True'



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


# def load_and_merge_swagger_files(output_file=None) -> Dict[str, Any]:
#     """Loads and merges all swagger YAML files from docs directory into single swagger spec."""
#     docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
#     merged_spec = {
#         'openapi': '3.0.0',
#         'info': {'title': 'Investment API', 'version': '1.0.0'},
#         'paths': {},
#         'components': {'schemas': {}, 'securitySchemes': {}}
#     }

#     def merge_component(source, target, component_type):
#         if source.get('components', {}).get(component_type):
#             target['components'][component_type].update(source['components'][component_type])

#     if not os.path.exists(docs_dir):
#         return merged_spec

#     for filename in os.listdir(docs_dir):
#         if not filename.endswith('.yml'):
#             continue
            
#         try:
#             with open(os.path.join(docs_dir, filename)) as f:
#                 spec = yaml.safe_load(f) or {}
                
#                 # Convert to OpenAPI 3.0 if needed
#                 if 'swagger' in spec:
#                     spec['openapi'] = '3.0.0'
#                     del spec['swagger']

#                 # Merge paths and components
#                 if spec.get('paths'):
#                     merged_spec['paths'].update(spec['paths'])
                
#                 merge_component(spec, merged_spec, 'schemas')
#                 merge_component(spec, merged_spec, 'securitySchemes')
                
#                 # Handle legacy Swagger 2.0 definitions
#                 if spec.get('definitions'):
#                     merged_spec['components']['schemas'].update(spec['definitions'])
                    
#         except Exception as e:
#             print(f"Error processing {filename}: {str(e)}")

#     if output_file:
#         try:
#             with open(output_file, 'w') as f:
#                 yaml.dump(merged_spec, f, sort_keys=False)
#         except Exception as e:
#             print(f"Error writing to {output_file}: {str(e)}")

#     return merged_spec

from flask import Flask
from utils.config import DevelopmentConfig, ProductionConfig, celery_init_app

import utils.dependency as dependency
from v1.auth.routes import auth_bp
from v1.profiles.routes import profile_bp
from utils.exceptions import exception_blueprint
from flask_cors import CORS
from v1.admin.routes import admin_bp
from v1.investments.routes import investment_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    #add extenstions 
    dependency.db.init_app(app)
    dependency.migrate.init_app(app, dependency.db)
    dependency.bcrypt.init_app(app)
    dependency.jwt.init_app(app)
    dependency.mail.init_app(app)
    CORS(app, resources={r"/investment/*": {"origins": "*"}}, supports_credentials=True)


    # Initialize Flasgger with the YAML file
    # print(load_and_merge_swagger_files())

    #register blueprints
    app.register_blueprint(exception_blueprint)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(investment_bp)

    app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
    app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"    
    celery_init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000, host="0.0.0.0")






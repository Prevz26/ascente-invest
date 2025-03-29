from flask import Flask
from utils.config import DevelopmentConfig, ProductionConfig, celery_init_app
import utils.dependency as dependency
from v1.auth.routes import auth_bp
def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    #add extenstions 
    dependency.db.init_app(app)
    dependency.bcrypt.init_app(app)
    dependency.jwt.init_app(app)
    dependency.mail.init_app(app)
    #register blueprints
    app.register_blueprint(auth_bp)

    app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
    app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"    
    celery_init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000)






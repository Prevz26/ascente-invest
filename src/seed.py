from utils.dependency import db
from main import create_app
from v1.profiles.models import *
from v1.investments.models import *
from v1.plans.models import *
app = create_app()

with app.app_context():
    db.create_all()
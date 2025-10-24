from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config
from app.models import db

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    limiter.init_app(app)
    
    with app.app_context():
        from app import routes
        app.register_blueprint(routes.bp)
        db.create_all()
    
    return app


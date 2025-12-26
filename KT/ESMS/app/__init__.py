from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.routes import auth, separation, checklist, scheduling, hierarchy
    app.register_blueprint(auth.bp)
    app.register_blueprint(separation.bp)
    app.register_blueprint(checklist.bp)
    app.register_blueprint(scheduling.bp)
    app.register_blueprint(hierarchy.bp)

    return app

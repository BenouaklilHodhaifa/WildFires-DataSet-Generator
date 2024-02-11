import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    load_dotenv()

    app = Flask("WildFires_Dataset_Generator", template_folder='app/templates', static_folder='app/static')  # Naming our application
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    CORS(app)
    
    db.init_app(app)

    # Main routes
    from app.services.main.routes import bp as main_bp
    app.register_blueprint(main_bp, url_prefix="/")

    # Datasets routes
    from app.services.datasets.routes import bp as datasets_bp
    app.register_blueprint(datasets_bp, url_prefix="/datasets")

    return app
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_cors import CORS

# db = SQLAlchemy()

def create_app():
    load_dotenv()

    app = Flask("WildFires_Dataset_Generator")  # Naming our application
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    # app.config['UPLOAD_FOLDER'] = 'storage/pictures'
    # app.config['PAGINATION_PER_PAGE'] = 5
    CORS(app)
    
    # db.init_app(app)

    from app.services.datasets.routes import bp as datasets_bp
    app.register_blueprint(datasets_bp, url_prefix="/datasets")

    return app
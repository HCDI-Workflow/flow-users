import logging
import os

from flask import Flask
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()
from flask_jwt_extended import JWTManager
from datetime import timedelta

logger = logging.getLogger()


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='D!l8oi-D830kjs13-23!38@!hd-$!#FLA2',
        DATABASE=os.path.join(app.instance_path, 'company.psql'),
    )
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=4)

    # Use cookies rather than header
    # app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    # app.config['JWT_COOKIE_SECURE'] = True  # Use True in production for HTTPS
    # app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # CSRF protection
    jwt = JWTManager(app)
    CORS(app)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        logger.error("Instance folder exists!")
    
    if test_config is None:
        app.config.from_pyfile('.env.py')
    else:
        app.config.from_mapping(test_config)
        
    return app
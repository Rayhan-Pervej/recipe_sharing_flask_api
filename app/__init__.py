from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import config

# Initialize extensions (without app instance)
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_name='development'):
    """
    Application factory function
    
    Args:
        config_name: Configuration to use (development/testing/production)
        
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)  # Enable CORS for all routes
    
    # Register blueprints
    from app.api.v1 import api_v1
    app.register_blueprint(api_v1)
    
    # Import models (for migrations to detect them)
    with app.app_context():
        from app.models import user, recipe, ingredient, category, rating
    
    # Root route for testing
    @app.route('/')
    def index():
        return {
            'message': 'Recipe Sharing API',
            'version': '1.0',
            'status': 'running'
        }
    
    return app
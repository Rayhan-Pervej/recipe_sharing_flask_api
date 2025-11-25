import os
from app import create_app

# Get config from environment or use default
config_name = os.getenv('FLASK_ENV', 'development')

# Create app instance
app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config['DEBUG']
    )
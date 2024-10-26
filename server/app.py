from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from models import db, User
from resources import api
from flask_cors import CORS  # Add this import

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Configure CORS
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True
    }
})

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Add this line
app.config['SESSION_COOKIE_SECURE'] = False     # Set to True in production
Session(app)

db.init_app(app)
migrate = Migrate(app, db)

api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
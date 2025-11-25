from app import db, bcrypt
from datetime import datetime
import sqlalchemy as sa


class User(db.Model):

    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)

    username = sa.Column(sa.String(80), unique=True, nullable=False, index=True)
    email = sa.Column(sa.String(120), unique=True, nullable=False, index=True)
    password_hash = sa.Column(sa.String(128), nullable=False)

    full_name = sa.Column(sa.String(100))
    bio = sa.Column(sa.Text)
    profile_image = sa.Column(sa.String(255))  
    is_admin = sa.Column(sa.Boolean, default=False)  
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic', cascade='all, delete-orphan') 
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, username, email, password, full_name=None): 
        self.username = username
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'recipe_count': self.recipes.count()
        }

        if include_email:
            data['email'] = self.email
        
        return data  
    
    def __repr__(self):
        return f"<User {self.username}>"
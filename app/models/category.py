from app import db
from datetime import datetime
import sqlalchemy as sa

class Category(db.Model):
    __tablename__ = "categories" 

    id = sa.Column(sa.Integer, primary_key=True)

    name = sa.Column(sa.String(50), unique=True, nullable=False, index=True)
    slug = sa.Column(sa.String(50), unique=True, nullable=False, index=True)
    description = sa.Column(sa.Text)

    image = sa.Column(sa.String(255))

    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)  
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  

    recipes = db.relationship('Recipe', backref='category', lazy='dynamic')  

    def __init__(self, name, description=None):
        self.name = name
        self.slug = self._generate_slug(name)
        self.description = description
    
    def _generate_slug(self, name):  
        return name.lower().replace(' ', '-').replace('_', '-')
    
    def to_dict(self, include_recipes=False):  
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'image': self.image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_recipes:
            data['recipe_count'] = self.recipes.count() if hasattr(self, 'recipes') else 0
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>' 
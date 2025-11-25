from app import db
from datetime import datetime
import sqlalchemy as sa


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = sa.Column(sa.Integer, primary_key=True)
    
    title = sa.Column(sa.String(200), nullable=False, index=True)
    slug = sa.Column(sa.String(200), unique=True, nullable=False, index=True)
    description = sa.Column(sa.Text)
    
    prep_time = sa.Column(sa.Integer)  
    cook_time = sa.Column(sa.Integer)  
    servings = sa.Column(sa.Integer)
    
    difficulty = sa.Column(sa.String(20)) 
    
    instructions = sa.Column(sa.Text, nullable=False)
    
    image = sa.Column(sa.String(255))
    
    is_published = sa.Column(sa.Boolean, default=False)
    
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    category_id = sa.Column(sa.Integer, sa.ForeignKey('categories.id'), nullable=False)
    

    ingredients = db.relationship('Ingredient', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, title, instructions, user_id, category_id, description=None):
        self.title = title
        self.slug = self._generate_slug(title)
        self.instructions = instructions
        self.user_id = user_id
        self.category_id = category_id
        self.description = description
    
    def _generate_slug(self, title):
        return title.lower().replace(' ', '-').replace('_', '-')
    
    def total_time(self):
        """Calculate total cooking time"""
        total = 0
        if self.prep_time:
            total += self.prep_time
        if self.cook_time:
            total += self.cook_time
        return total
    
    def average_rating(self):
        """Calculate average rating"""
        if self.ratings.count() == 0:
            return 0
        total = sum([rating.score for rating in self.ratings])
        return round(total / self.ratings.count(), 2)
    
    def to_dict(self, include_author=False, include_ingredients=False, include_ratings=False):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'total_time': self.total_time(),
            'servings': self.servings,
            'difficulty': self.difficulty,
            'instructions': self.instructions,
            'image': self.image,
            'is_published': self.is_published,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'average_rating': self.average_rating(),
            'rating_count': self.ratings.count()
        }
        
        if include_author:
            data['author'] = self.author.to_dict() if self.author else None
        
        if include_ingredients:
            data['ingredients'] = [ingredient.to_dict() for ingredient in self.ingredients]
        
        if include_ratings:
            data['ratings'] = [rating.to_dict() for rating in self.ratings]
        
        return data
    
    def __repr__(self):
        return f'<Recipe {self.title}>'
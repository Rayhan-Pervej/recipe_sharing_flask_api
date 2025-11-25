from app import db
from datetime import datetime
import sqlalchemy as sa


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = sa.Column(sa.Integer, primary_key=True)
    
    score = sa.Column(sa.Integer, nullable=False)  
    comment = sa.Column(sa.Text) 
    
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
 
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey('recipes.id'), nullable=False)
    
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_rating'),
    )
    
    def __init__(self, score, user_id, recipe_id, comment=None):
        self.score = score
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.comment = comment
    
    def validate_score(self):
        """Validate that score is between 1 and 5"""
        if self.score < 1 or self.score > 5:
            raise ValueError("Rating score must be between 1 and 5")
    
    def to_dict(self, include_user=False, include_recipe=False):
        data = {
            'id': self.id,
            'score': self.score,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'recipe_id': self.recipe_id
        }
        
        if include_user:
            data['user'] = self.user.to_dict() if self.user else None
        
        if include_recipe:
            data['recipe'] = self.recipe.to_dict() if self.recipe else None
        
        return data
    
    def __repr__(self):
        return f'<Rating {self.score}/5 by User {self.user_id} for Recipe {self.recipe_id}>'
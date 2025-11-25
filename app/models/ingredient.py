from app import db
from datetime import datetime
import sqlalchemy as sa

class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = sa.Column(sa.Integer, primary_key= True)

    name= sa.Column(sa.String(100), nullable=False)
    quantity= sa.Column(sa.String(50), nullable=False)
    unit = sa.Column(sa.String(20))
    notes = sa.Column(sa.Text)
    
    order = sa.Column(sa.Integer, default=0)
    created_at = sa.Column(sa.DateTime, default= datetime.utcnow, nullable=False)

    recipe_id = sa.Column(sa.Integer, sa.ForeignKey('recipes.id'), nullable=False)
    
    def __init__(self, name, quantity, recipe_id, unit=None, notes=None, order=0):
        self.name = name
        self.quantity = quantity
        self.recipe_id = recipe_id
        self.unit = unit
        self.notes = notes
        self.order = order
    
    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes,
            'order': self.order,
            'recipe_id': self.recipe_id
        }
        return data
    
    def __repr__(self):
        return f'<Ingredient {self.name} - {self.quantity}>'
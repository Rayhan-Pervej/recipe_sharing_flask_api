from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
from sqlalchemy import desc


class RecipeCreateSchema(Schema):
    """Schema for creating a new recipe"""
    title = fields.Str(required=True, validate=[
        validate.Length(min=3, max=200),
        validate.Regexp(r'^\S.*\S$|^\S$', error="Title cannot be empty or only whitespace")
    ])
    description = fields.Str(allow_none=True)
    instructions = fields.Str(required=True, validate=validate.Length(min=10))
    prep_time = fields.Int(validate=validate.Range(min=0), allow_none=True)
    cook_time = fields.Int(validate=validate.Range(min=0), allow_none=True)
    servings = fields.Int(validate=validate.Range(min=1), allow_none=True)
    difficulty = fields.Str(
        validate=validate.OneOf(['easy', 'medium', 'hard']),
        allow_none=True
    )
    category_id = fields.Int(required=True)
    image = fields.Str(validate=validate.Length(max=255), allow_none=True)
    is_published = fields.Bool(load_default=False)


class RecipeUpdateSchema(Schema):
    """Schema for updating a recipe - all fields optional"""
    title = fields.Str(validate=[
        validate.Length(min=3, max=200),
        validate.Regexp(r'^\S.*\S$|^\S$', error="Title cannot be empty or only whitespace")
    ])
    description = fields.Str(allow_none=True)
    instructions = fields.Str(validate=validate.Length(min=10))
    prep_time = fields.Int(validate=validate.Range(min=0), allow_none=True)
    cook_time = fields.Int(validate=validate.Range(min=0), allow_none=True)
    servings = fields.Int(validate=validate.Range(min=1), allow_none=True)
    difficulty = fields.Str(
        validate=validate.OneOf(['easy', 'medium', 'hard']),
        allow_none=True
    )
    category_id = fields.Int()
    image = fields.Str(validate=validate.Length(max=255), allow_none=True)
    is_published = fields.Bool()


class RecipeResponseSchema(Schema):
    """Schema for recipe list responses with summary data"""
    id = fields.Int(dump_only=True)
    title = fields.Str()
    slug = fields.Str()
    description = fields.Str()
    prep_time = fields.Int()
    cook_time = fields.Int()
    servings = fields.Int()
    difficulty = fields.Str()
    image = fields.Str()
    is_published = fields.Bool()
    created_at = fields.DateTime(format='iso', dump_only=True)
    updated_at = fields.DateTime(format='iso', dump_only=True)
    
    # Foreign keys
    user_id = fields.Int()
    category_id = fields.Int()
    
    # Computed fields
    total_time = fields.Method("get_total_time")
    ingredient_count = fields.Method("get_ingredient_count")
    average_rating = fields.Method("get_average_rating")
    rating_count = fields.Method("get_rating_count")
    
    # Related data
    author = fields.Method("get_author_info")
    category = fields.Method("get_category_info")
    
    def get_total_time(self, obj):
        """Calculate total cooking time"""
        if obj.prep_time and obj.cook_time:
            return obj.prep_time + obj.cook_time
        return obj.prep_time or obj.cook_time
    
    def get_ingredient_count(self, obj):
        """Get count of ingredients"""
        return obj.ingredients.count() if hasattr(obj, 'ingredients') else 0
    
    def get_average_rating(self, obj):
        """Get average rating score"""
        if hasattr(obj, 'average_rating'):
            # Check if it's a method or property
            avg = obj.average_rating() if callable(obj.average_rating) else obj.average_rating
            return round(avg, 2) if avg else None
        return None
    
    def get_rating_count(self, obj):
        """Get total number of ratings"""
        return obj.ratings.count() if hasattr(obj, 'ratings') else 0
    
    def get_author_info(self, obj):
        """Get basic author information"""
        if hasattr(obj, 'user') and obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email
            }
        return None
    
    def get_category_info(self, obj):
        """Get basic category information"""
        if hasattr(obj, 'category') and obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'slug': obj.category.slug
            }
        return None


class IngredientNestedSchema(Schema):
    """Nested schema for ingredients in recipe detail"""
    id = fields.Int()
    name = fields.Str()
    quantity = fields.Str()
    unit = fields.Str()
    notes = fields.Str()
    order = fields.Int()


class RatingNestedSchema(Schema):
    """Nested schema for ratings in recipe detail"""
    id = fields.Int()
    score = fields.Int()
    comment = fields.Str()
    created_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')
    user = fields.Method("get_user_info")
    
    def get_user_info(self, obj):
        """Get user information for the rating"""
        if hasattr(obj, 'user') and obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username
            }
        return None


class RecipeDetailResponseSchema(RecipeResponseSchema):
    """Schema for detailed recipe response including full ingredients and ratings"""
    instructions = fields.Str()
    
    # Full related data
    ingredients = fields.Method("get_ingredients_list")
    ratings = fields.Method("get_ratings_list")
    
    def get_ingredients_list(self, obj):
        """Get full list of ingredients ordered"""
        if hasattr(obj, 'ingredients'):
            ingredients = obj.ingredients.order_by('order').all()
            return IngredientNestedSchema(many=True).dump(ingredients)
        return []
    
    def get_ratings_list(self, obj):
        """Get list of ratings ordered by date"""
        if hasattr(obj, 'ratings'):
            ratings = obj.ratings.order_by(desc('created_at')).all()
            return RatingNestedSchema(many=True).dump(ratings)
        return []


# Create schema instances
recipe_create_schema = RecipeCreateSchema()
recipe_update_schema = RecipeUpdateSchema()
recipe_response_schema = RecipeResponseSchema()
recipes_response_schema = RecipeResponseSchema(many=True)
recipe_detail_response_schema = RecipeDetailResponseSchema()
from marshmallow import Schema, fields, validate, validates, ValidationError


class RatingCreateSchema(Schema):
    """Schema for creating a new rating"""
    score = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=5, error="Score must be between 1 and 5")
    )
    comment = fields.Str(validate=validate.Length(max=500), allow_none=True)


class RatingUpdateSchema(Schema):
    """Schema for updating a rating - all fields optional"""
    score = fields.Int(
        validate=validate.Range(min=1, max=5, error="Score must be between 1 and 5")
    )
    comment = fields.Str(validate=validate.Length(max=500), allow_none=True)


class RatingResponseSchema(Schema):
    """Schema for rating response"""
    id = fields.Int(dump_only=True)
    score = fields.Int()
    comment = fields.Str()
    created_at = fields.DateTime(format='iso', dump_only=True)
    updated_at = fields.DateTime(format='iso', dump_only=True)
    user_id = fields.Int()
    recipe_id = fields.Int()
    
    # Related data
    user = fields.Method("get_user_info")
    recipe = fields.Method("get_recipe_info")
    
    def get_user_info(self, obj):
        """Get basic user information"""
        if hasattr(obj, 'user') and obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email
            }
        return None
    
    def get_recipe_info(self, obj):
        """Get basic recipe information"""
        if hasattr(obj, 'recipe') and obj.recipe:
            return {
                'id': obj.recipe.id,
                'title': obj.recipe.title,
                'slug': obj.recipe.slug
            }
        return None


# Create schema instances
rating_create_schema = RatingCreateSchema()
rating_update_schema = RatingUpdateSchema()
rating_response_schema = RatingResponseSchema()
ratings_response_schema = RatingResponseSchema(many=True)
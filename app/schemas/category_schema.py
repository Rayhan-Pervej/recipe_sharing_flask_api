from marshmallow import Schema, fields, validate

class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    description = fields.Str(validate=validate.Length(max=500))
    image = fields.Str(validate=validate.Length(max=255))


class CategoryUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=50))
    description = fields.Str(validate=validate.Length(max=500))
    image = fields.Str(validate=validate.Length(max=255))


class CategoryResponseSchema(Schema):
    
    id = fields.Int(dump_only=True)
    name = fields.Str()
    slug = fields.Str()
    description = fields.Str()
    image = fields.Str()
    created_at = fields.DateTime(format='iso', dump_only=True)
    updated_at = fields.DateTime(format='iso', dump_only=True)
    
    recipe_count = fields.Method("get_recipe_count")
    
    def get_recipe_count(self, obj):
        return obj.recipes.count() if hasattr(obj, 'recipes') else 0
    


category_create_schema = CategoryCreateSchema()
category_update_schema = CategoryUpdateSchema()
category_response_schema = CategoryResponseSchema()
categories_response_schema = CategoryResponseSchema(many=True)
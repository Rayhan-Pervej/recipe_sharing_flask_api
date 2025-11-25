from marshmallow import Schema, fields, validate, ValidationError


class IngredientCreateSchema(Schema):

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    quantity = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    unit = fields.Str(validate=validate.Length(max=20), allow_none=True)
    notes = fields.Str(allow_none=True)
    order = fields.Int(validate=validate.Range(min=0), load_default=0)


class IngredientUpdateSchema(Schema):

    name = fields.Str(validate=validate.Length(min=1, max=100))
    quantity = fields.Str(validate=validate.Length(min=1, max=50))
    unit = fields.Str(validate=validate.Length(max=20), allow_none=True)
    notes = fields.Str(allow_none=True)
    order = fields.Int(validate=validate.Range(min=0))


class IngredientResponseSchema(Schema):

    id = fields.Int(dump_only=True)
    name = fields.Str()
    quantity = fields.Str()
    unit = fields.Str()
    notes = fields.Str()
    order = fields.Int()
    recipe_id = fields.Int()
    created_at = fields.DateTime(format='iso', dump_only=True)


class IngredientBulkCreateSchema(Schema):

    ingredients = fields.List(
        fields.Nested(IngredientCreateSchema),
        required=True,
        validate=validate.Length(min=1, max=50)
    )


class IngredientBulkUpdateSchema(Schema):

    ingredients = fields.List(
        fields.Dict(),
        required=True,
        validate=validate.Length(min=1, max=50)
    )


# Create schema instances
ingredient_create_schema = IngredientCreateSchema()
ingredient_update_schema = IngredientUpdateSchema()
ingredient_response_schema = IngredientResponseSchema()
ingredients_response_schema = IngredientResponseSchema(many=True)
ingredient_bulk_create_schema = IngredientBulkCreateSchema()
ingredient_bulk_update_schema = IngredientBulkUpdateSchema()
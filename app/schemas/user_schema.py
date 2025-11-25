"""
User Validation Schemas using Marshmallow
"""
from marshmallow import Schema, fields, validates, ValidationError, validate
from app.utils.validators import validate_email, validate_password, validate_username


class UserRegistrationSchema(Schema):
    """Schema for user registration"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    full_name = fields.Str(validate=validate.Length(max=100))
    
    @validates('username')
    def validate_username_format(self, value, **kwargs):
        """Validate username format"""
        result = validate_username(value)
        if not result['valid']:
            raise ValidationError(result['errors'][0])
    
    @validates('password')
    def validate_password_strength(self, value, **kwargs):
        """Validate password strength"""
        result = validate_password(value)
        if not result['valid']:
            raise ValidationError(result['errors'][0])


class UserLoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class UserUpdateSchema(Schema):
    """Schema for user profile update"""
    full_name = fields.Str(validate=validate.Length(max=100))
    bio = fields.Str()
    profile_image = fields.Str(validate=validate.Length(max=255))


class UserResponseSchema(Schema):
    """Schema for user response (output) - serializes User model objects"""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    full_name = fields.Str()
    bio = fields.Str()
    profile_image = fields.Str()
    is_admin = fields.Bool()
    created_at = fields.DateTime(format='iso', dump_only=True)
    
    # Custom field to get recipe count
    recipe_count = fields.Method("get_recipe_count")
    
    def get_recipe_count(self, obj):
        """Get the count of recipes for this user"""
        return obj.recipes.count() if hasattr(obj, 'recipes') else 0


class PasswordChangeSchema(Schema):
    """Schema for password change"""
    old_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    
    @validates('new_password')
    def validate_new_password_strength(self, value, **kwargs):
        """Validate new password strength"""
        result = validate_password(value)
        if not result['valid']:
            raise ValidationError(result['errors'][0])


# Create instances for easy import
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_update_schema = UserUpdateSchema()
user_response_schema = UserResponseSchema()
password_change_schema = PasswordChangeSchema()
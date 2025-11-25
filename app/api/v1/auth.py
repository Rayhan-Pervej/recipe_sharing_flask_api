from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.user import User
from app.schemas.user_schema import(
    user_registration_schema,
    user_login_schema,
    user_response_schema
)

from app.utils.responses import(
    success_response,
    error_response,
    validation_error_response,
    unauthorized_response,
)

class RegisterResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            if not data:
                return error_response(message="No input data provided", status_code=400)
            
            validated_data = user_registration_schema.load(data)

            existing_user = User.query.filter(
                (User.email == validated_data['email']) | 
                (User.username == validated_data['username'])
            ).first()

            if existing_user:
                if existing_user.email == validated_data['email']:
                    return error_response(
                        message="User with this email already exists",
                        status_code=400
                    )
                else:
                    return error_response(
                        message="User with this username already exists",
                        status_code=400
                    )
            
            new_user = User(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                full_name=validated_data.get('full_name')
            )

            db.session.add(new_user)
            db.session.commit()

            access_token = create_access_token(identity=str(new_user.id))
            refresh_token = create_refresh_token(identity=str(new_user.id))


            # CORRECT: Pass User object directly to schema
            user_data = user_response_schema.dump(new_user)

            response_data = {
                'user': user_data,
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return success_response(
                data=response_data,
                message="User registered successfully",
                status_code=201
            )
        
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        
        except IntegrityError:
            db.session.rollback()
            return error_response(
                message="User with this email or username already exists",
                status_code=400
            )
        
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"An error occurred during registration: {str(e)}",
                status_code=500
            )
        
class LoginResource(Resource):

    def post(self):
        try:
            data = request.get_json()
            
            if not data:
                return error_response(message="No input data provided", status_code=400)
            
            validated_data = user_login_schema.load(data)
            
            user = User.query.filter_by(email=validated_data['email']).first()
            
            if not user or not user.check_password(validated_data['password']):
                return unauthorized_response(message="Invalid email or password")
            
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))



            
            # CORRECT: Pass User object directly to schema
            user_data = user_response_schema.dump(user)
            
            response_data = {
                'user': user_data,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
            return success_response(
                data=response_data,
                message="Login successful",
                status_code=200
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        
        except Exception as e:
            return error_response(
                message=f"An error occurred during login: {str(e)}",
                status_code=500
            )
        
class RefreshTokenResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            
            new_access_token = create_access_token(identity=str(current_user_id))

            
            response_data = {
                'access_token': new_access_token
            }
            
            return success_response(
                data=response_data,
                message="Access token refreshed successfully",
                status_code=200
            )
            
        except Exception as e:
            return unauthorized_response(message=f"Token refresh failed: {str(e)}")


class LogoutResource(Resource):
    
    @jwt_required()
    def post(self):
        
        return success_response(
            message="Logout successful. Please remove tokens from client.",
            status_code=200
        )


class UserProfileResource(Resource):

    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            
            user = User.query.get(current_user_id)
            
            if not user:
                return error_response(message="User not found", status_code=404)
            
            # CORRECT: Pass User object directly to schema
            user_data = user_response_schema.dump(user)
            
            return success_response(
                data=user_data,
                message="Profile retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"An error occurred: {str(e)}",
                status_code=500
            )
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.category import Category
from app.models.user import User
from app.schemas.category_schema import (
    category_create_schema,
    category_update_schema,
    category_response_schema,
    categories_response_schema
)
from app.utils.responses import (
    success_response,
    error_response,
    validation_error_response,
    not_found_response,
    forbidden_response
)

class CategoryListResource(Resource):

    def get(self):

        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            # include_recipes = request.args.get('include_recipes', 'false').lower() == 'true'

            if page < 1:
                page = 1
            if per_page < 1 or per_page >100:
                per_page = 10

            pagination = Category.query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            categories_data = categories_response_schema.dump(pagination.items)


            response_data = {
                'categories': categories_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total
                }
            }

            return success_response(
                data= response_data,
                message="Categories retrieved successfully",
                status_code=200
            )
        
        except Exception as e:
            return error_response(
                message=f"An error occurred: {str(e)}",
                status_code=500
            )
        

    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user or not user.is_admin:
                return forbidden_response(message="Admin privileges required to create categories")
            data = request.get_json()

            if not data:
                return error_response(message="No input data provided", status_code=400)
            
            validated_data = category_create_schema.load(data)

            existing_category = Category.query.filter_by(name=validated_data['name']).first()

            if existing_category:
                return error_response(
                    message="Category with this name already exists",
                    status_code=400
                )
            new_category = Category(
                name=validated_data['name'],
                description=validated_data.get('description')
            )

            if 'image' in validated_data:
                new_category.image = validated_data['image']

            db.session.add(new_category)
            db.session.commit()

            category_data = category_response_schema.dump(new_category)

            return success_response(
                data=category_data,
                message="Category created successfully",
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        
        except IntegrityError:
            db.session.rollback()
            return error_response(
                message="Category with this name already exists",
                status_code=400
            )
        
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"An error occurred: {str(e)}",
                status_code=500
            )
        

class CategoryDetailResource(Resource):
    def get(self, category_id):
        try:
            category = Category.query.get(category_id)
            if not category:
                return not_found_response(message="Category not found")
            
            category_data = category_response_schema.dump(category)
            
            return success_response(
                data=category_data,
                message="Category retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"An error occurred: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def put(self, category_id):
        try:
            # Check if user is admin
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_admin:
                return forbidden_response(message="Admin privileges required to update categories")
            
            
            category = Category.query.get(category_id)
            
            if not category:
                return not_found_response(message="Category not found")
            
            
            data = request.get_json()
            
            if not data:
                return error_response(message="No input data provided", status_code=400)
            
           
            validated_data = category_update_schema.load(data)
            
            
            if 'name' in validated_data:
                existing_category = Category.query.filter(
                    Category.name == validated_data['name'],
                    Category.id != category_id
                ).first()
                
                if existing_category:
                    return error_response(
                        message="Another category with this name already exists",
                        status_code=400
                    )
                
                category.name = validated_data['name']
                category.slug = category._generate_slug(validated_data['name'])
            
            
            if 'description' in validated_data:
                category.description = validated_data['description']
            
            if 'image' in validated_data:
                category.image = validated_data['image']
            
            db.session.commit()
            
            
            category_data = category_response_schema.dump(category)
            
            return success_response(
                data=category_data,
                message="Category updated successfully",
                status_code=200
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        
        except IntegrityError:
            db.session.rollback()
            return error_response(
                message="Category with this name already exists",
                status_code=400
            )
        
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"An error occurred: {str(e)}",
                status_code=500
            )
        
    @jwt_required()
    def delete(self, category_id):
       
        try:
           
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_admin:
                return forbidden_response(message="Admin privileges required to delete categories")
            
           
            category = Category.query.get(category_id)
            
            if not category:
                return not_found_response(message="Category not found")
            
            
            recipe_count = category.recipes.count() if hasattr(category, 'recipes') else 0
            if recipe_count > 0:
                return error_response(
                    message=f"Cannot delete category with {recipe_count} recipe(s). Please reassign or delete recipes first.",
                    status_code=400
                )
            
            db.session.delete(category)
            db.session.commit()
            
            return success_response(
                message="Category deleted successfully",
                status_code=200
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"An error occurred: {str(e)}",
                status_code=500
            )
        
class CategorySearchResource(Resource):

    def get(self):
        try:
            search_query = request.args.get('q', '').strip()
            
            if not search_query:
                return error_response(
                    message="Search query parameter 'q' is required",
                    status_code=400
                )
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 10
            
            pagination = Category.query.filter(
                Category.name.ilike(f'%{search_query}%')
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            categories_data = categories_response_schema.dump(pagination.items)
            
            response_data = {
                'categories': categories_data,
                'search_query': search_query,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total_pages': pagination.pages,
                    'total_items': pagination.total
                }
            }
            
            return success_response(
                data=response_data,
                message=f"Found {pagination.total} category(ies)",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"An error occurred: {str(e)}",
                status_code=500
            )





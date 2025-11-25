from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.recipe import Recipe
from app.models.user import User
from app.models.category import Category
from app.schemas.recipe_schema import (
    recipe_create_schema,
    recipe_update_schema,
    recipe_response_schema,
    recipes_response_schema,
    recipe_detail_response_schema
)
from app.utils.responses import (
    success_response,
    error_response,
    validation_error_response,
    not_found_response,
    unauthorized_response,
    forbidden_response
)


class RecipeListResource(Resource):
    """Resource for listing and creating recipes"""
    
    def get(self):
        """Get list of recipes with filters and pagination (Public)"""
        try:
            # Pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            per_page = min(per_page, 100)  # Max 100 items per page
            
            # Filter parameters
            category_id = request.args.get('category_id', type=int)
            difficulty = request.args.get('difficulty', type=str)
            user_id = request.args.get('user_id', type=int)
            is_published = request.args.get('is_published', type=str)
            search = request.args.get('search', type=str)
            
            # Build query
            query = Recipe.query
            
            # Apply filters
            if category_id:
                query = query.filter_by(category_id=category_id)
            
            if difficulty and difficulty in ['easy', 'medium', 'hard']:
                query = query.filter_by(difficulty=difficulty)
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            # Published filter - default to show only published for non-owners
            if is_published:
                if is_published.lower() in ['true', '1', 'yes']:
                    query = query.filter_by(is_published=True)
                elif is_published.lower() in ['false', '0', 'no']:
                    query = query.filter_by(is_published=False)
            else:
                # By default, only show published recipes
                query = query.filter_by(is_published=True)
            
            # Search by title
            if search:
                query = query.filter(Recipe.title.ilike(f'%{search}%'))
            
            # Order by creation date (newest first)
            query = query.order_by(Recipe.created_at.desc())
            
            # Paginate
            paginated_recipes = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Serialize recipes
            recipes_data = recipes_response_schema.dump(paginated_recipes.items)
            
            # Build response with pagination metadata
            response_data = {
                'recipes': recipes_data,
                'pagination': {
                    'page': paginated_recipes.page,
                    'per_page': paginated_recipes.per_page,
                    'total_pages': paginated_recipes.pages,
                    'total_items': paginated_recipes.total,
                }
            }
            
            return success_response(
                data=response_data,
                message="Recipes retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving recipes: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def post(self):
        """Create a new recipe (Authenticated users only)"""
        try:
            current_user_id = get_jwt_identity()
            
            # Get JSON data
            json_data = request.get_json()
            if not json_data:
                return error_response(
                    message="No input data provided",
                    status_code=400
                )
            
            # Validate input data
            validated_data = recipe_create_schema.load(json_data)
            
            # Verify category exists
            category = Category.query.get(validated_data['category_id'])
            if not category:
                return not_found_response(message="Category not found")
            
            # Create new recipe using the model's __init__
            new_recipe = Recipe(
                title=validated_data['title'],
                instructions=validated_data['instructions'],
                user_id=current_user_id,
                category_id=validated_data['category_id'],
                description=validated_data.get('description')
            )
            
            # Set the slug properly
            new_slug = validated_data['title'].lower().replace(' ', '-')
            import re
            new_slug = re.sub(r'[^a-z0-9-]', '', new_slug)
            new_slug = re.sub(r'-+', '-', new_slug).strip('-')
            
            # Ensure slug is unique
            base_slug = new_slug
            counter = 1
            while Recipe.query.filter_by(slug=new_slug).first():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            
            new_recipe.slug = new_slug
            
            # Set optional fields
            new_recipe.prep_time = validated_data.get('prep_time')
            new_recipe.cook_time = validated_data.get('cook_time')
            new_recipe.servings = validated_data.get('servings')
            new_recipe.difficulty = validated_data.get('difficulty')
            new_recipe.image = validated_data.get('image')
            new_recipe.is_published = validated_data.get('is_published', False)
            
            db.session.add(new_recipe)
            db.session.commit()
            
            # Serialize response
            recipe_data = recipe_response_schema.dump(new_recipe)
            
            return success_response(
                data=recipe_data,
                message="Recipe created successfully",
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error creating recipe: {str(e)}",
                status_code=500
            )


class RecipeDetailResource(Resource):
    """Resource for getting, updating, and deleting a specific recipe"""
    
    def get(self, recipe_id):
        """Get a specific recipe by ID (Public)"""
        try:
            recipe = Recipe.query.get(recipe_id)
            
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Check if recipe is published or user is owner
            # For GET, we allow viewing unpublished recipes by their owners
            # But for public users, only published recipes are visible
            if not recipe.is_published:
                # Check if user is authenticated and is the owner
                from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
                try:
                    verify_jwt_in_request(optional=True)
                    current_user_id = get_jwt_identity()
                    if current_user_id != recipe.user_id:
                        # Check if admin
                        user = User.query.get(current_user_id)
                        if not (user and user.is_admin):
                            return forbidden_response(
                                message="This recipe is not published"
                            )
                except:
                    return forbidden_response(
                        message="This recipe is not published"
                    )
            
            # Serialize with full details (ingredients and ratings)
            recipe_data = recipe_detail_response_schema.dump(recipe)
            
            return success_response(
                data=recipe_data,
                message="Recipe retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving recipe: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def put(self, recipe_id):
        """Update a recipe (Owner or Admin only)"""
        try:
            current_user_id = get_jwt_identity()
            
            # Get recipe
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Check permissions
            user = User.query.get(current_user_id)
            if recipe.user_id != current_user_id and not user.is_admin:
                return forbidden_response(
                    message="You don't have permission to update this recipe"
                )
            
            # Get JSON data
            json_data = request.get_json()
            if not json_data:
                return error_response(
                    message="No input data provided",
                    status_code=400
                )
            
            # Validate input data
            validated_data = recipe_update_schema.load(json_data)
            
            # If category_id is being updated, verify it exists
            if 'category_id' in validated_data:
                category = Category.query.get(validated_data['category_id'])
                if not category:
                    return not_found_response(message="Category not found")
            
            # Update title and slug if title is changed
            if 'title' in validated_data and validated_data['title'] != recipe.title:
                # Create slug from title (simple version without slugify library)
                new_slug = validated_data['title'].lower().replace(' ', '-')
                # Remove special characters
                import re
                new_slug = re.sub(r'[^a-z0-9-]', '', new_slug)
                new_slug = re.sub(r'-+', '-', new_slug).strip('-')
                
                # Ensure new slug is unique
                base_slug = new_slug
                counter = 1
                while Recipe.query.filter(
                    Recipe.slug == new_slug,
                    Recipe.id != recipe_id
                ).first():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                
                recipe.slug = new_slug
            
            # Update fields
            for key, value in validated_data.items():
                setattr(recipe, key, value)
            
            db.session.commit()
            
            # Serialize response
            recipe_data = recipe_response_schema.dump(recipe)
            
            return success_response(
                data=recipe_data,
                message="Recipe updated successfully",
                status_code=200
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error updating recipe: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def delete(self, recipe_id):
        """Delete a recipe (Owner or Admin only)"""
        try:
            current_user_id = get_jwt_identity()
            
            # Get recipe
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Check permissions
            user = User.query.get(current_user_id)
            if recipe.user_id != current_user_id and not user.is_admin:
                return forbidden_response(
                    message="You don't have permission to delete this recipe"
                )
            
            # Delete recipe (cascade will delete ingredients and ratings)
            db.session.delete(recipe)
            db.session.commit()
            
            return success_response(
                data=None,
                message="Recipe deleted successfully",
                status_code=200
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error deleting recipe: {str(e)}",
                status_code=500
            )


class RecipesByUserResource(Resource):
    """Resource for getting all recipes by a specific user"""
    
    def get(self, user_id):
        """Get all recipes by a specific user (Public)"""
        try:
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                return not_found_response(message="User not found")
            
            # Pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            per_page = min(per_page, 100)
            
            # Filter parameters
            is_published = request.args.get('is_published', type=str)
            
            # Build query
            query = Recipe.query.filter_by(user_id=user_id)
            
            # Published filter
            if is_published:
                if is_published.lower() in ['true', '1', 'yes']:
                    query = query.filter_by(is_published=True)
                elif is_published.lower() in ['false', '0', 'no']:
                    query = query.filter_by(is_published=False)
            else:
                # By default, only show published recipes
                query = query.filter_by(is_published=True)
            
            # Order by creation date (newest first)
            query = query.order_by(Recipe.created_at.desc())
            
            # Paginate
            paginated_recipes = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Serialize recipes
            recipes_data = recipes_response_schema.dump(paginated_recipes.items)
            
            # Build response with pagination metadata
            response_data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'recipes': recipes_data,
                'pagination': {
                    'page': paginated_recipes.page,
                    'per_page': paginated_recipes.per_page,
                    'total_pages': paginated_recipes.pages,
                    'total_items': paginated_recipes.total,
                }
            }
            
            return success_response(
                data=response_data,
                message=f"Recipes by {user.username} retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving user recipes: {str(e)}",
                status_code=500
            )


class RecipesByCategoryResource(Resource):
    """Resource for getting all recipes in a specific category"""
    
    def get(self, category_id):
        """Get all recipes in a specific category (Public)"""
        try:
            # Verify category exists
            category = Category.query.get(category_id)
            if not category:
                return not_found_response(message="Category not found")
            
            # Pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            per_page = min(per_page, 100)
            
            # Filter parameters
            difficulty = request.args.get('difficulty', type=str)
            search = request.args.get('search', type=str)
            
            # Build query - only published recipes
            query = Recipe.query.filter_by(
                category_id=category_id,
                is_published=True
            )
            
            # Apply additional filters
            if difficulty and difficulty in ['easy', 'medium', 'hard']:
                query = query.filter_by(difficulty=difficulty)
            
            if search:
                query = query.filter(Recipe.title.ilike(f'%{search}%'))
            
            # Order by creation date (newest first)
            query = query.order_by(Recipe.created_at.desc())
            
            # Paginate
            paginated_recipes = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Serialize recipes
            recipes_data = recipes_response_schema.dump(paginated_recipes.items)
            
            # Build response with pagination metadata
            response_data = {
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'description': category.description
                },
                'recipes': recipes_data,
                'pagination': {
                    'page': paginated_recipes.page,
                    'per_page': paginated_recipes.per_page,
                    'total_pages': paginated_recipes.pages,
                    'total_items': paginated_recipes.total,
                }
            }
            
            return success_response(
                data=response_data,
                message=f"Recipes in category '{category.name}' retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving category recipes: {str(e)}",
                status_code=500
            )
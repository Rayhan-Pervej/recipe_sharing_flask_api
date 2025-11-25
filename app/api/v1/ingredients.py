from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.ingredient_schema import (
    ingredient_create_schema,
    ingredient_update_schema,
    ingredient_response_schema,
    ingredients_response_schema,
    ingredient_bulk_create_schema
)
from app.utils.responses import (
    success_response,
    error_response,
    validation_error_response,
    not_found_response,
    forbidden_response
)


class IngredientListResource(Resource):
    
    def get(self, recipe_id):
       
        try:
       
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
          
            ingredients = Ingredient.query.filter_by(recipe_id=recipe_id).order_by(Ingredient.order).all()
            

            ingredients_data = ingredients_response_schema.dump(ingredients)
            
            response_data = {
                'recipe_id': recipe_id,
                'recipe_title': recipe.title,
                'ingredients': ingredients_data,
                'total_ingredients': len(ingredients)
            }
            
            return success_response(
                data=response_data,
                message="Ingredients retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving ingredients: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def post(self, recipe_id):
       
        try:
            current_user_id = get_jwt_identity()
            

            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            
            user = User.query.get(current_user_id)
            if recipe.user_id != current_user_id and not user.is_admin:
                return forbidden_response(
                    message="You don't have permission to add ingredients to this recipe"
                )
            
            
            data = request.get_json()
            if not data:
                return error_response(
                    message="No input data provided",
                    status_code=400
                )
            
       
            validated_data = ingredient_create_schema.load(data)
            

            new_ingredient = Ingredient(
                name=validated_data['name'],
                quantity=validated_data['quantity'],
                recipe_id=recipe_id,
                unit=validated_data.get('unit'),
                notes=validated_data.get('notes'),
                order=validated_data.get('order', 0)
            )
            
            db.session.add(new_ingredient)
            db.session.commit()
            
            
            ingredient_data = ingredient_response_schema.dump(new_ingredient)
            
            return success_response(
                data=ingredient_data,
                message="Ingredient added successfully",
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error adding ingredient: {str(e)}",
                status_code=500
            )


class IngredientDetailResource(Resource):
  
    
    def get(self, recipe_id, ingredient_id):
       
        try:
       
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
         
            ingredient = Ingredient.query.filter_by(
                id=ingredient_id,
                recipe_id=recipe_id
            ).first()
            
            if not ingredient:
                return not_found_response(message="Ingredient not found")
            
           
            ingredient_data = ingredient_response_schema.dump(ingredient)
            
            return success_response(
                data=ingredient_data,
                message="Ingredient retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving ingredient: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def put(self, recipe_id, ingredient_id):
       
        try:
            current_user_id = get_jwt_identity()
            
         
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
     
            user = User.query.get(current_user_id)
            if recipe.user_id != current_user_id and not user.is_admin:
                return forbidden_response(
                    message="You don't have permission to update ingredients in this recipe"
                )
            
        
            ingredient = Ingredient.query.filter_by(
                id=ingredient_id,
                recipe_id=recipe_id
            ).first()
            
            if not ingredient:
                return not_found_response(message="Ingredient not found")
            
           
            data = request.get_json()
            if not data:
                return error_response(
                    message="No input data provided",
                    status_code=400
                )
            
         
            validated_data = ingredient_update_schema.load(data)
            
          
            if 'name' in validated_data:
                ingredient.name = validated_data['name']
            if 'quantity' in validated_data:
                ingredient.quantity = validated_data['quantity']
            if 'unit' in validated_data:
                ingredient.unit = validated_data['unit']
            if 'notes' in validated_data:
                ingredient.notes = validated_data['notes']
            if 'order' in validated_data:
                ingredient.order = validated_data['order']
            
            db.session.commit()
            
            
            ingredient_data = ingredient_response_schema.dump(ingredient)
            
            return success_response(
                data=ingredient_data,
                message="Ingredient updated successfully",
                status_code=200
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error updating ingredient: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def delete(self, recipe_id, ingredient_id):
     
        try:
            current_user_id = get_jwt_identity()
            
           
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
           
            user = User.query.get(current_user_id)
            if recipe.user_id != current_user_id and not user.is_admin:
                return forbidden_response(
                    message="You don't have permission to delete ingredients from this recipe"
                )
            
           
            ingredient = Ingredient.query.filter_by(
                id=ingredient_id,
                recipe_id=recipe_id
            ).first()
            
            if not ingredient:
                return not_found_response(message="Ingredient not found")
            
            
            db.session.delete(ingredient)
            db.session.commit()
            
            return success_response(
                data=None,
                message="Ingredient deleted successfully",
                status_code=200
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error deleting ingredient: {str(e)}",
                status_code=500
            )


class IngredientBulkCreateResource(Resource):

    
    @jwt_required()
    def post(self, recipe_id):
       
        try:
            current_user_id = get_jwt_identity()
            
            
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
          
            user = User.query.get(current_user_id)
            if recipe.user_id != current_user_id and not user.is_admin:
                return forbidden_response(
                    message="You don't have permission to add ingredients to this recipe"
                )
            
            
            json_data = request.get_json()
            if not json_data:
                return error_response(
                    message="No input data provided",
                    status_code=400
                )
            
           
            validated_data = ingredient_bulk_create_schema.load(json_data)
            
            
            new_ingredients = []
            for idx, ingredient_data in enumerate(validated_data['ingredients']):
                new_ingredient = Ingredient(
                    name=ingredient_data['name'],
                    quantity=ingredient_data['quantity'],
                    recipe_id=recipe_id,
                    unit=ingredient_data.get('unit'),
                    notes=ingredient_data.get('notes'),
                    order=ingredient_data.get('order', idx)
                )
                new_ingredients.append(new_ingredient)
            
           
            db.session.add_all(new_ingredients)
            db.session.commit()
            
           
            ingredients_data = ingredients_response_schema.dump(new_ingredients)
            
            response_data = {
                'recipe_id': recipe_id,
                'ingredients': ingredients_data,
                'total_added': len(new_ingredients)
            }
            
            return success_response(
                data=response_data,
                message=f"{len(new_ingredients)} ingredients added successfully",
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error adding ingredients: {str(e)}",
                status_code=500
            )


class IngredientBulkUpdateResource(Resource):
  
    
    @jwt_required()
    def put(self, recipe_id):
 
        try:
            current_user_id = get_jwt_identity()
            
           
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
           
            user = User.query.get(current_user_id)
            if recipe.user_id != current_user_id and not user.is_admin:
                return forbidden_response(
                    message="You don't have permission to update ingredients for this recipe"
                )
            
           
            json_data = request.get_json()
            if not json_data or 'ingredients' not in json_data:
                return error_response(
                    message="No input data provided or missing 'ingredients' field",
                    status_code=400
                )
            
            ingredients_list = json_data.get('ingredients', [])
            
            if not isinstance(ingredients_list, list) or len(ingredients_list) == 0:
                return error_response(
                    message="Ingredients must be a non-empty list",
                    status_code=400
                )
            
          
            updated_ingredients = []
            for ingredient_data in ingredients_list:
                if 'id' not in ingredient_data:
                    continue
                
                ingredient = Ingredient.query.filter_by(
                    id=ingredient_data['id'],
                    recipe_id=recipe_id
                ).first()
                
                if ingredient:
                    
                    if 'name' in ingredient_data:
                        ingredient.name = ingredient_data['name']
                    if 'quantity' in ingredient_data:
                        ingredient.quantity = ingredient_data['quantity']
                    if 'unit' in ingredient_data:
                        ingredient.unit = ingredient_data['unit']
                    if 'notes' in ingredient_data:
                        ingredient.notes = ingredient_data['notes']
                    if 'order' in ingredient_data:
                        ingredient.order = ingredient_data['order']
                    
                    updated_ingredients.append(ingredient)
            
            db.session.commit()
            
          
            ingredients_data = ingredients_response_schema.dump(updated_ingredients)
            
            response_data = {
                'recipe_id': recipe_id,
                'ingredients': ingredients_data,
                'total_updated': len(updated_ingredients)
            }
            
            return success_response(
                data=response_data,
                message=f"{len(updated_ingredients)} ingredients updated successfully",
                status_code=200
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error updating ingredients: {str(e)}",
                status_code=500
            )
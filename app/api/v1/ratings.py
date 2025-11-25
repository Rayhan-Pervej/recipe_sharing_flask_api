from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc

from app import db
from app.models.rating import Rating
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.rating_schema import (
    rating_create_schema,
    rating_update_schema,
    rating_response_schema,
    ratings_response_schema
)
from app.utils.responses import (
    success_response,
    error_response,
    validation_error_response,
    not_found_response,
    forbidden_response
)


class RatingListResource(Resource):
    """Resource for listing and creating ratings for a recipe"""
    
    def get(self, recipe_id):
        """Get all ratings for a recipe (Public)"""
        try:
            # Verify recipe exists
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            per_page = min(per_page, 100)
            
            # Get ratings ordered by creation date (newest first)
            query = Rating.query.filter_by(recipe_id=recipe_id).order_by(desc(Rating.created_at))
            
            # Paginate
            paginated_ratings = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Serialize ratings
            ratings_data = ratings_response_schema.dump(paginated_ratings.items)
            
            response_data = {
                'recipe_id': recipe_id,
                'recipe_title': recipe.title,
                'ratings': ratings_data,
                'pagination': {
                    'page': paginated_ratings.page,
                    'per_page': paginated_ratings.per_page,
                    'total_pages': paginated_ratings.pages,
                    'total_items': paginated_ratings.total,
                    'has_next': paginated_ratings.has_next,
                    'has_prev': paginated_ratings.has_prev
                }
            }
            
            return success_response(
                data=response_data,
                message="Ratings retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving ratings: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def post(self, recipe_id):
        """Add a rating to a recipe (Authenticated users, one rating per user per recipe)"""
        try:
            current_user_id = get_jwt_identity()
            
            # Verify recipe exists
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Check if user already rated this recipe
            existing_rating = Rating.query.filter_by(
                user_id=current_user_id,
                recipe_id=recipe_id
            ).first()
            
            if existing_rating:
                return error_response(
                    message="You have already rated this recipe. Use PUT to update your rating.",
                    status_code=400
                )
            
            # Get JSON data
            json_data = request.get_json()
            if not json_data:
                return error_response(
                    message="No input data provided",
                    status_code=400
                )
            
            # Validate input data
            validated_data = rating_create_schema.load(json_data)
            
            # Create new rating
            new_rating = Rating(
                score=validated_data['score'],
                comment=validated_data.get('comment'),
                user_id=current_user_id,
                recipe_id=recipe_id
            )
            
            db.session.add(new_rating)
            db.session.commit()
            
            # Serialize response
            rating_data = rating_response_schema.dump(new_rating)
            
            return success_response(
                data=rating_data,
                message="Rating added successfully",
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        except IntegrityError:
            db.session.rollback()
            return error_response(
                message="You have already rated this recipe",
                status_code=400
            )
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error adding rating: {str(e)}",
                status_code=500
            )


class RatingDetailResource(Resource):
    """Resource for getting, updating, and deleting a specific rating"""
    
    def get(self, recipe_id, rating_id):
        """Get a specific rating (Public)"""
        try:
            # Verify recipe exists
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Get rating
            rating = Rating.query.filter_by(
                id=rating_id,
                recipe_id=recipe_id
            ).first()
            
            if not rating:
                return not_found_response(message="Rating not found")
            
            # Serialize rating
            rating_data = rating_response_schema.dump(rating)
            
            return success_response(
                data=rating_data,
                message="Rating retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving rating: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def put(self, recipe_id, rating_id):
        """Update a rating (Rating owner only)"""
        try:
            current_user_id = get_jwt_identity()
            
            # Verify recipe exists
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Get rating
            rating = Rating.query.filter_by(
                id=rating_id,
                recipe_id=recipe_id
            ).first()
            
            if not rating:
                return not_found_response(message="Rating not found")
            
            # Check if user is the rating owner
            if rating.user_id != current_user_id:
                return forbidden_response(
                    message="You can only update your own ratings"
                )
            
            # Get JSON data
            json_data = request.get_json()
            if not json_data:
                return error_response(
                    message="No input data provided",
                    status_code=400
                )
            
            # Validate input data
            validated_data = rating_update_schema.load(json_data)
            
            # Update fields
            for key, value in validated_data.items():
                setattr(rating, key, value)
            
            db.session.commit()
            
            # Serialize response
            rating_data = rating_response_schema.dump(rating)
            
            return success_response(
                data=rating_data,
                message="Rating updated successfully",
                status_code=200
            )
            
        except ValidationError as e:
            return validation_error_response(errors=e.messages)
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error updating rating: {str(e)}",
                status_code=500
            )
    
    @jwt_required()
    def delete(self, recipe_id, rating_id):
        """Delete a rating (Rating owner only)"""
        try:
            current_user_id = get_jwt_identity()
            
            # Verify recipe exists
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Get rating
            rating = Rating.query.filter_by(
                id=rating_id,
                recipe_id=recipe_id
            ).first()
            
            if not rating:
                return not_found_response(message="Rating not found")
            
            # Check if user is the rating owner
            if rating.user_id != current_user_id:
                return forbidden_response(
                    message="You can only delete your own ratings"
                )
            
            # Delete rating
            db.session.delete(rating)
            db.session.commit()
            
            return success_response(
                data=None,
                message="Rating deleted successfully",
                status_code=200
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(
                message=f"Error deleting rating: {str(e)}",
                status_code=500
            )


class UserRatingsResource(Resource):
    """Resource for getting all ratings by a specific user"""
    
    def get(self, user_id):
        """Get all ratings by a specific user (Public)"""
        try:
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                return not_found_response(message="User not found")
            
            # Pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            per_page = min(per_page, 100)
            
            # Get ratings ordered by creation date (newest first)
            query = Rating.query.filter_by(user_id=user_id).order_by(desc(Rating.created_at))
            
            # Paginate
            paginated_ratings = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Serialize ratings
            ratings_data = ratings_response_schema.dump(paginated_ratings.items)
            
            response_data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'ratings': ratings_data,
                'pagination': {
                    'page': paginated_ratings.page,
                    'per_page': paginated_ratings.per_page,
                    'total_pages': paginated_ratings.pages,
                    'total_items': paginated_ratings.total,
                    'has_next': paginated_ratings.has_next,
                    'has_prev': paginated_ratings.has_prev
                }
            }
            
            return success_response(
                data=response_data,
                message=f"Ratings by {user.username} retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving user ratings: {str(e)}",
                status_code=500
            )


class RecipeRatingStatsResource(Resource):
    """Resource for getting rating statistics for a recipe"""
    
    def get(self, recipe_id):
        """Get rating statistics for a recipe (Public)"""
        try:
            # Verify recipe exists
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return not_found_response(message="Recipe not found")
            
            # Get all ratings for this recipe
            ratings = Rating.query.filter_by(recipe_id=recipe_id).all()
            
            if not ratings:
                response_data = {
                    'recipe_id': recipe_id,
                    'recipe_title': recipe.title,
                    'total_ratings': 0,
                    'average_rating': None,
                    'distribution': {
                        '5_stars': 0,
                        '4_stars': 0,
                        '3_stars': 0,
                        '2_stars': 0,
                        '1_star': 0
                    }
                }
                
                return success_response(
                    data=response_data,
                    message="No ratings yet for this recipe",
                    status_code=200
                )
            
            # Calculate statistics
            total_ratings = len(ratings)
            average_rating = sum([r.score for r in ratings]) / total_ratings
            
            # Calculate distribution
            distribution = {
                '5_stars': len([r for r in ratings if r.score == 5]),
                '4_stars': len([r for r in ratings if r.score == 4]),
                '3_stars': len([r for r in ratings if r.score == 3]),
                '2_stars': len([r for r in ratings if r.score == 2]),
                '1_star': len([r for r in ratings if r.score == 1])
            }
            
            # Calculate percentages
            distribution_percentages = {
                '5_stars': round((distribution['5_stars'] / total_ratings) * 100, 1),
                '4_stars': round((distribution['4_stars'] / total_ratings) * 100, 1),
                '3_stars': round((distribution['3_stars'] / total_ratings) * 100, 1),
                '2_stars': round((distribution['2_stars'] / total_ratings) * 100, 1),
                '1_star': round((distribution['1_star'] / total_ratings) * 100, 1)
            }
            
            response_data = {
                'recipe_id': recipe_id,
                'recipe_title': recipe.title,
                'total_ratings': total_ratings,
                'average_rating': round(average_rating, 2),
                'distribution': distribution,
                'distribution_percentages': distribution_percentages
            }
            
            return success_response(
                data=response_data,
                message="Rating statistics retrieved successfully",
                status_code=200
            )
            
        except Exception as e:
            return error_response(
                message=f"Error retrieving rating statistics: {str(e)}",
                status_code=500
            )
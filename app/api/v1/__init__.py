from flask import Blueprint
from flask_restful import Api
from app.api.v1.auth import (
    RegisterResource,
    LoginResource,
    RefreshTokenResource,
    LogoutResource,
    UserProfileResource
)


from app.api.v1.categories import (
    CategoryListResource,
    CategoryDetailResource,
    CategorySearchResource
)

from app.api.v1.recipes import (
    RecipeListResource,
    RecipeDetailResource,
    RecipesByUserResource,
    RecipesByCategoryResource
)

from app.api.v1.ingredients import (
    IngredientListResource,
    IngredientDetailResource,
    IngredientBulkCreateResource,
    IngredientBulkUpdateResource
)

from app.api.v1.ratings import (
    RatingListResource,
    RatingDetailResource,
    UserRatingsResource,
    RecipeRatingStatsResource
)

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1/')
api = Api(api_v1)


# authentication routes
api.add_resource(RegisterResource, '/auth/register')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(RefreshTokenResource, '/auth/refresh')
api.add_resource(LogoutResource, '/auth/logout')
api.add_resource(UserProfileResource, '/auth/profile')

# category routes
api.add_resource(CategoryListResource, '/categories')
api.add_resource(CategoryDetailResource, '/categories/<int:category_id>')
api.add_resource(CategorySearchResource, '/categories/search')

# recipe routes
api.add_resource(RecipeListResource, '/recipes')
api.add_resource(RecipeDetailResource, '/recipes/<int:recipe_id>')
api.add_resource(RecipesByUserResource, '/recipes/user/<int:user_id>')
api.add_resource(RecipesByCategoryResource, '/recipes/category/<int:category_id>')

# ingredient routes (nested under recipes)
api.add_resource(IngredientListResource, '/recipes/<int:recipe_id>/ingredients')
api.add_resource(IngredientDetailResource, '/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>')
api.add_resource(IngredientBulkCreateResource, '/recipes/<int:recipe_id>/ingredients/bulk')
api.add_resource(IngredientBulkUpdateResource, '/recipes/<int:recipe_id>/ingredients/bulk-update')

# rating routes (nested under recipes)
api.add_resource(RatingListResource, '/recipes/<int:recipe_id>/ratings')
api.add_resource(RatingDetailResource, '/recipes/<int:recipe_id>/ratings/<int:rating_id>')
api.add_resource(RecipeRatingStatsResource, '/recipes/<int:recipe_id>/ratings/stats')

# user rating routes
api.add_resource(UserRatingsResource, '/users/<int:user_id>/ratings')
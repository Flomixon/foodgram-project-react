from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (
    FollowViewSet,
    IngredientsViewSet,
    RecipeViewSet,
    TagViewSet,
    favorite_recipe,
    shopping_cart,
    shopping_cart_txt,
    subscribe
)

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientsViewSet)
router_v1.register('recipes', RecipeViewSet)
router_v1.register('users/subscriptions', FollowViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', favorite_recipe),
    path('recipes/<int:recipe_id>/shopping_cart/', shopping_cart),
    path('recipes/download_shopping_cart/', shopping_cart_txt),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:user_id>/subscribe/', subscribe),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
]

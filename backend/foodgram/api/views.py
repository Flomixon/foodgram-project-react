from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, DestroyAPIView
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from api.serializers import (
    FollowerSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    RecipeViewSerializer,
    ShoppingCartSerializer,
    TagSerializer
)

from users.models import Follow
from recipes.models import (
    Favorite,
    Ingredients,
    Recipe,
    ShoppingCart,
    Tag,
    User
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'ingredients', 'tags'
    ).all()
    serializer_class = RecipeViewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        if self.request.user.is_authenticated:
            user = self.request.user
            if 'is_favorited' in params:
                if params['is_favorited']:
                    queryset = queryset.filter(
                        id__in=user.favorites.values_list('recipe', flat=True)
                    )
            elif 'is_in_shopping_cart' in params:
                if params['is_in_shopping_cart']:
                    queryset = queryset.filter(
                        id__in=user.user_shopps.values_list(
                            'recipe', flat=True)
                    )
            elif 'author' in params:
                author = get_object_or_404(User, id=params['author'])
                queryset = author.recipes.all()
        if 'tags' in params:
            return queryset.filter(
                tags__slug__in=params.getlist('tags')
            ).distinct()
        return queryset

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'POST',):
            return RecipeSerializer
        return RecipeViewSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ShoppingCartViewSet(CreateAPIView, DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, recipe_id):
        user = request.user
        try:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            res = ShoppingCartSerializer(recipe)
            return Response(res.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                data={"errors": 'Рецепт уже добавлен в корзину!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(ShoppingCart, user=user, recipe=recipe_id)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipeViewSet(CreateAPIView, DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, recipe_id):
        try:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            Favorite.objects.create(user=request.user, recipe=recipe)
            res = ShoppingCartSerializer(recipe)
            return Response(res.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                data={"errors": 'Рецепт уже добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, recipe_id):
        recipe = get_object_or_404(
            Favorite, user=request.user, recipe=recipe_id
        )
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = FollowerSerializer
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(
            id__in=user.follower.values_list('author', flat=True)
        )


class SubscribeViewSet(CreateAPIView, DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, user_id):
        user = request.user
        sub = get_object_or_404(User, id=user_id)
        try:
            Follow.objects.create(user=user, author=sub)
            res = FollowerSerializer(sub, context={'request': request})
            return Response(data=res.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                data={"errors": 'Вы уже подписаны на автора!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as error:
            return Response(
                data={"errors": error},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, user_id):
        user = request.user
        sub = get_object_or_404(User, id=user_id)
        try:
            remove = user.follower.get(author=sub)
            remove.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                data={"errors": 'Вы не подписаны на данного пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


def shopping_cart_txt(request):
    if request.user.is_authenticated:
        user = request.user
        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping_cart.txt'
        shop_list = {}
        recipes = user.user_shopps.all()
        for recipe in recipes:
            for ingred in recipe.recipe.recipes_ingr.all():
                key = (f'{ingred.ingredients} '
                       f'({ingred.ingredients.measurement_unit}) - ')
                if key in shop_list:
                    shop_list[key] += ingred.amount
                else:
                    shop_list[key] = ingred.amount
        for k, v in shop_list.items():
            response.writelines(f'{k}{v}\n')
        return response
    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

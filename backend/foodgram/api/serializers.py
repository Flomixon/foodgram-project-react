import base64

from django.core.files.base import ContentFile
from django.db import transaction

from rest_framework import serializers

from recipes.models import Ingredients, Recipe, RecipeIngredients, ShoppingCart, Tag, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS)+(
            'id', 'email', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        req = self.context.get('request')
        user = req.user
        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug',)
        model = Tag


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


class RecipeIngredViewSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id',
        source='ingredients'
    )
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
        source='ingredients'
    )
    measurement_unit = serializers.SlugRelatedField(
        read_only=True,
        slug_field='measurement_unit',
        source='ingredients'
    )
    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount',)
        model = RecipeIngredients


class RecipeViewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredViewSerializer(many=True, read_only=True, source='recipes_ingr')
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image',
            'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart'
        )
        model = Recipe

    def get_is_favorited(self, obj):
        req = self.context.get('request')
        user = req.user
        if user.is_authenticated:
            return user.favorites.filter(recipe=obj).exists()
        return False
    
    def get_is_in_shopping_cart(self, obj):
        req = self.context.get('request')
        user = req.user
        if user.is_authenticated:
            return user.user_shopps.filter(recipe=obj).exists()
        return False


class RecipeIngredSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
            queryset= Ingredients.objects.all(),
            source='ingredients'
        )
    
    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredients


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
            queryset=Tag.objects.all(),
            many=True
        )

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        model = Recipe

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                    recipe=recipe,
                    **ingredient
                )
        recipe.tags.set(tags)
        recipe.save()
        return recipe
    
    def to_representation(self, instance):
        res = RecipeViewSerializer(instance, context={'request': self.context.get('request')})
        return res.data
    

class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe

    
class FollowerSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = ShoppingCartSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        fields = tuple(User.REQUIRED_FIELDS)+(
            'id', 'email', 'is_subscribed', 'recipes', 'recipes_count'
        )
        model = User

    def get_is_subscribed(self, obj):
        req = self.context.get('request')
        user = req.user
        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()
        return False
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()


from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

# Create your models here.
User = get_user_model()


class Tag(models.Model):
    '''Модель тегов'''
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'Цвет в HEX',
        validators=(
            RegexValidator(r'^#([A-F0-9]{6})$'),
        ),
        max_length=7
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredients(models.Model):
    '''Модель ингредиентов'''
    name = models.CharField(
        max_length=200,
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    '''Модель рецептов'''
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='recipes',
        verbose_name='Рецепт',
    )
    name = models.CharField(
        'Название',
        max_length=200
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        default=None
        )
    text = models.TextField(
        'Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        related_name='ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag'
    )
    cooking_time = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredients(models.Model):
    '''Модель ингредиентов для рецептов'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_ingr'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_recipe_ingredients'
            ),
        )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_tag'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tags'
    )

    class Meta:
        constraints=(
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag'
            ),
        )


class Follow(models.Model):
    '''Модель подписок'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follower'
            ),
        )


class Favorite(models.Model):
    '''Модель избранных рецептов'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_users'
    )


class SgoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopps',
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingred_lists'
    )
    quantity = models.PositiveSmallIntegerField()

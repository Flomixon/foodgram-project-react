from django.contrib import admin
from recipes.models import (
    Favorite, Follow, Ingredients, ShoppingCart,
    Tag, Recipe, RecipeIngredients, RecipeTag, User
)


admin.site.register(Favorite)
admin.site.register(Follow)
admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredients)
admin.site.register(RecipeTag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'added_in_favorite')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author', 'name')

    def added_in_favorite(self, obj):
        return obj.favorite_users.count()
    
    added_in_favorite.short_description = 'Добавлено в избранное'
    


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')

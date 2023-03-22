from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import TagViewSet


router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet)

urlpatterns = [
    # path('users/?P<user_id>[1-9]\d*', вьюха),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router_v1.urls)),
]

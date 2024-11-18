from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, TaskViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, TaskViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')  # Endpunkt für Benutzer
router.register(r'contacts', ContactViewSet, basename='contact')  # Endpunkt für Kontakte
router.register(r'tasks', TaskViewSet, basename='task')  # Endpunkt für Aufgaben

urlpatterns = [
    path('', include(router.urls)),
]
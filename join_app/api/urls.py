from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, TaskViewSet, UserViewSet, SubtaskViewSet, TaskContactViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')  # Endpunkt für Benutzer
router.register(r'contacts', ContactViewSet, basename='contact')  # Endpunkt für Kontakte
router.register(r'tasks', TaskViewSet, basename='task')  # Endpunkt für Aufgaben

urlpatterns = [

    path('', include(router.urls)),
    path('tasks/<int:task_id>/subtasks/', SubtaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-subtasks'),
    path('tasks/<int:task_id>/subtasks/<int:pk>/', SubtaskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='task-subtask-detail'),
    path('tasks/<int:task_id>/contacts/', TaskContactViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-contacts'),
    path('tasks/<int:task_id>/contacts/<int:pk>/', TaskContactViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='task-contact-detail'),
    ]
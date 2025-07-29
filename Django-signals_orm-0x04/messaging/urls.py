from django.urls import path, include
from rest_framework_nested import routers
from .views import UserViewSet, MessageViewSet, NotificationViewSet, MessageHistoryViewSet

router = routers.DefaultRouter()
router.register('messages', MessageViewSet, basename='message')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('users', UserViewSet, basename='user')
router.register('message-history', MessageHistoryViewSet, basename='message-history')

urlpatterns = [
    path('', include(router.urls)),
]
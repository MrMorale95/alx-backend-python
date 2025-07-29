from django.urls import path, include
from .views import ConversationViewSet, MessageViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('conversations', ConversationViewSet, basename='conversation')

conversation_router = routers.NestedDefaultRouter(router, 'conversations', lookup='conversation')
conversation_router.register('messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]
import django_filters
from .models import Message, Conversation, User


class MessageFilter(django_filters.FilterSet):
    # Filter messages by sender, conversation, and date
    sender = django_filters.UUIDFilter(field_name='sender__user_id')
    conversation = django_filters.UUIDFilter(field_name='conversation__conversation_id')
    sent_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lt')
    sent_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gt')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'sent_before', 'sent_after']


class ConversationFilter(django_filters.FilterSet):
    # Filter by user ID of a participant
    participant = django_filters.UUIDFilter(method='filter_by_participant')

    class Meta:
        model = Conversation
        fields = ['participant']

    def filter_by_participant(self, queryset, name, value):
        return queryset.filter(participants__user_id=value)

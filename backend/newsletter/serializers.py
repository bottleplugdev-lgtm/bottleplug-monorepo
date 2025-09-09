from rest_framework import serializers
from .models import NewsletterSubscription, NewsletterCampaign

class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = NewsletterSubscription
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'status', 'preferences', 'subscribed_at', 'unsubscribed_at',
            'updated_at', 'last_email_sent', 'email_count', 'open_count',
            'click_count', 'source', 'ip_address', 'user_agent', 'is_active'
        ]
        read_only_fields = [
            'subscribed_at', 'unsubscribed_at', 'updated_at',
            'last_email_sent', 'email_count', 'open_count', 'click_count',
            'source', 'ip_address', 'user_agent'
        ]

class NewsletterCampaignSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    open_rate = serializers.ReadOnlyField()
    click_rate = serializers.ReadOnlyField()
    bounce_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = NewsletterCampaign
        fields = [
            'id', 'title', 'subject', 'content', 'html_content',
            'status', 'scheduled_at', 'sent_at', 'recipient_count',
            'sent_count', 'opened_count', 'clicked_count', 'bounced_count',
            'from_name', 'from_email', 'reply_to', 'track_opens',
            'track_clicks', 'created_by', 'created_at', 'updated_at',
            'open_rate', 'click_rate', 'bounce_rate'
        ]
        read_only_fields = [
            'sent_at', 'recipient_count', 'sent_count', 'opened_count',
            'clicked_count', 'bounced_count', 'created_by', 'created_at', 'updated_at'
        ]

class NewsletterSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    source = serializers.CharField(max_length=100, required=False, default='website')

class NewsletterUnsubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField() 
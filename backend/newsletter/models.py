from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone

class NewsletterSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
    ]
    
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Preferences
    preferences = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email tracking
    last_email_sent = models.DateTimeField(null=True, blank=True)
    email_count = models.PositiveIntegerField(default=0)
    open_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    
    # Source tracking
    source = models.CharField(max_length=100, blank=True)  # website, mobile, admin, etc.
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['status', 'subscribed_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return self.email
    
    def unsubscribe(self):
        self.status = 'unsubscribed'
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def reactivate(self):
        self.status = 'active'
        self.unsubscribed_at = None
        self.save()
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""

class NewsletterCampaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Recipients
    recipient_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    opened_count = models.PositiveIntegerField(default=0)
    clicked_count = models.PositiveIntegerField(default=0)
    bounced_count = models.PositiveIntegerField(default=0)
    
    # Campaign settings
    from_name = models.CharField(max_length=100, default='Wine Soirée')
    from_email = models.EmailField(default='noreply@winesoiree.com')
    reply_to = models.EmailField(blank=True)
    
    # Tracking
    track_opens = models.BooleanField(default=True)
    track_clicks = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def open_rate(self):
        if self.sent_count > 0:
            return (self.opened_count / self.sent_count) * 100
        return 0
    
    @property
    def click_rate(self):
        if self.sent_count > 0:
            return (self.clicked_count / self.sent_count) * 100
        return 0
    
    @property
    def bounce_rate(self):
        if self.sent_count > 0:
            return (self.bounced_count / self.sent_count) * 100
        return 0

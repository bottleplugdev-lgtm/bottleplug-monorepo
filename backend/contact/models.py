from django.db import models
from django.core.validators import EmailValidator

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('order', 'Order Question'),
        ('product', 'Product Question'),
        ('event', 'Event Question'),
        ('feedback', 'Feedback'),
        ('complaint', 'Complaint'),
        ('partnership', 'Partnership'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Contact information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True)
    
    # Message details
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    subject_custom = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # Response tracking
    responded_at = models.DateTimeField(null=True, blank=True)
    response_message = models.TextField(blank=True)
    responded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Newsletter subscription
    subscribe_newsletter = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['subject', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_subject_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_subject(self):
        if self.subject == 'other' and self.subject_custom:
            return self.subject_custom
        return self.get_subject_display()
    
    @property
    def is_new(self):
        return self.status == 'new'
    
    @property
    def is_resolved(self):
        return self.status == 'resolved'
    
    @property
    def response_time(self):
        if self.responded_at and self.created_at:
            return self.responded_at - self.created_at
        return None
    
    def mark_as_responded(self, response_message, user=None):
        from django.utils import timezone
        self.status = 'resolved'
        self.response_message = response_message
        self.responded_at = timezone.now()
        if user:
            self.responded_by = user
        self.save()
    
    def mark_as_in_progress(self, user=None):
        self.status = 'in_progress'
        if user:
            self.responded_by = user
        self.save()
    
    def close_message(self, user=None):
        self.status = 'closed'
        if user:
            self.responded_by = user
        self.save()

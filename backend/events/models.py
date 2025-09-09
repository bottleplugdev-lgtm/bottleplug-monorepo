from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class Event(models.Model):
    EVENT_TYPES = [
        ('tasting', 'Wine Tasting'),
        ('dinner', 'Wine Dinner'),
        ('class', 'Wine Class'),
        ('tour', 'Vineyard Tour'),
        ('party', 'Wine Party'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Date and time
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Location
    location_name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    
    # Capacity and pricing
    max_capacity = models.PositiveIntegerField()
    current_attendees = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    member_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Event details
    featured_wines = models.TextField(blank=True)
    food_pairings = models.TextField(blank=True)
    dress_code = models.CharField(max_length=100, blank=True)
    age_requirement = models.PositiveIntegerField(default=21)
    
    # Images
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    gallery = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO
    slug = models.SlugField(unique=True, max_length=200)
    meta_description = models.CharField(max_length=300, blank=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['event_type', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now() and self.status == 'published'
    
    @property
    def is_full(self):
        return self.current_attendees >= self.max_capacity
    
    @property
    def available_spots(self):
        return max(0, self.max_capacity - self.current_attendees)
    
    @property
    def is_cancelled(self):
        return self.status == 'cancelled'
    
    @property
    def is_completed(self):
        return self.end_date < timezone.now() or self.status == 'completed'

class RSVP(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Guest information
    guest_count = models.PositiveIntegerField(default=1)
    guest_names = models.JSONField(default=list, blank=True)
    dietary_restrictions = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    
    # Payment
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        # Update event attendee count when RSVP status changes
        if self.pk:
            old_instance = RSVP.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                if old_instance.status == 'confirmed' and self.status != 'confirmed':
                    self.event.current_attendees = max(0, self.event.current_attendees - old_instance.guest_count)
                elif self.status == 'confirmed' and old_instance.status != 'confirmed':
                    self.event.current_attendees += self.guest_count
                self.event.save()
        else:
            # New RSVP
            if self.status == 'confirmed':
                self.event.current_attendees += self.guest_count
                self.event.save()
        
        super().save(*args, **kwargs)
    
    @property
    def is_confirmed(self):
        return self.status == 'confirmed'
    
    @property
    def is_cancelled(self):
        return self.status == 'cancelled'
    
    @property
    def is_attended(self):
        return self.status == 'attended'

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Device(models.Model):
    """Water meter device model"""
    device_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    api_key = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    is_active = models.BooleanField(default=True)
    installation_date = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    # Device specifications
    pulse_rate = models.FloatField(default=450.0, help_text="Pulses per liter")
    
    def __str__(self):
        return f"{self.name} ({self.device_id})"
    
    class Meta:
        ordering = ['-installation_date']


class WaterUsage(models.Model):
    """Water usage reading model"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(default=timezone.now)
    flow_rate = models.FloatField(help_text="Liters per minute")
    total_consumption = models.FloatField(help_text="Total liters consumed")
    pulse_count = models.IntegerField(help_text="Raw pulse count from sensor")
    
    # Calculated fields
    daily_consumption = models.FloatField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.device.name} - {self.timestamp} - {self.total_consumption}L"
    
    def save(self, *args, **kwargs):
        # Calculate cost based on consumption
        from django.conf import settings
        if self.total_consumption:
            self.cost = self.total_consumption * settings.WATER_RATE_PER_LITER
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]


class Alert(models.Model):
    """Alert model for leak detection and excessive usage"""
    ALERT_TYPES = [
        ('leak', 'Leak Detected'),
        ('excessive', 'Excessive Usage'),
        ('offline', 'Device Offline'),
        ('maintenance', 'Maintenance Required'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Alert specific data
    threshold_value = models.FloatField(null=True, blank=True)
    actual_value = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.device.name} - {self.get_alert_type_display()} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']


class UserProfile(models.Model):
    """Extended user profile for water meter system"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Billing preferences
    billing_cycle = models.CharField(max_length=20, default='monthly', 
                                   choices=[('weekly', 'Weekly'), ('monthly', 'Monthly')])
    
    def __str__(self):
        return f"{self.user.username} Profile"


class Bill(models.Model):
    """Monthly/weekly billing model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='bills')
    
    # Billing period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Usage data
    total_consumption = models.FloatField(help_text="Total liters consumed in period")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Bill status
    is_paid = models.BooleanField(default=False)
    generated_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Bill for {self.user.username} - {self.start_date} to {self.end_date}"
    
    class Meta:
        ordering = ['-generated_at']
        unique_together = ['user', 'device', 'start_date', 'end_date']

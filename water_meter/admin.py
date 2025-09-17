from django.contrib import admin
from .models import Device, WaterUsage, Alert, UserProfile, Bill


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'name', 'location', 'owner', 'is_active', 'last_seen']
    list_filter = ['is_active', 'installation_date', 'owner']
    search_fields = ['device_id', 'name', 'location', 'owner__username']
    readonly_fields = ['api_key', 'installation_date']
    
    fieldsets = (
        ('Device Information', {
            'fields': ('device_id', 'name', 'location', 'owner')
        }),
        ('Configuration', {
            'fields': ('pulse_rate', 'is_active')
        }),
        ('System', {
            'fields': ('api_key', 'installation_date', 'last_seen'),
            'classes': ('collapse',)
        })
    )


@admin.register(WaterUsage)
class WaterUsageAdmin(admin.ModelAdmin):
    list_display = ['device', 'timestamp', 'flow_rate', 'total_consumption', 'cost']
    list_filter = ['device', 'timestamp']
    search_fields = ['device__name', 'device__device_id']
    readonly_fields = ['cost']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('device')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['device', 'alert_type', 'severity', 'timestamp', 'is_resolved']
    list_filter = ['alert_type', 'severity', 'is_resolved', 'timestamp']
    search_fields = ['device__name', 'message']
    readonly_fields = ['timestamp']
    
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
    mark_resolved.short_description = "Mark selected alerts as resolved"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'billing_cycle', 'email_notifications', 'sms_notifications']
    list_filter = ['billing_cycle', 'email_notifications', 'sms_notifications']
    search_fields = ['user__username', 'user__email', 'phone_number']


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['user', 'device', 'start_date', 'end_date', 'total_consumption', 'total_cost', 'is_paid']
    list_filter = ['is_paid', 'generated_at', 'device']
    search_fields = ['user__username', 'device__name']
    readonly_fields = ['generated_at']
    date_hierarchy = 'start_date'

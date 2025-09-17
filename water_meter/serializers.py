from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Device, WaterUsage, Alert, UserProfile, Bill


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class DeviceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Device
        fields = ['device_id', 'name', 'location', 'owner', 'is_active', 
                 'installation_date', 'last_seen', 'pulse_rate']
        read_only_fields = ['api_key', 'installation_date', 'last_seen']


class WaterUsageSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_location = serializers.CharField(source='device.location', read_only=True)
    
    class Meta:
        model = WaterUsage
        fields = ['id', 'device', 'device_name', 'device_location', 'timestamp', 
                 'flow_rate', 'total_consumption', 'pulse_count', 'daily_consumption', 'cost']
        read_only_fields = ['id', 'cost', 'daily_consumption']


class WaterUsageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating water usage records from IoT devices"""
    device_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = WaterUsage
        fields = ['device_id', 'flow_rate', 'total_consumption', 'pulse_count', 'timestamp']
    
    def create(self, validated_data):
        device_id = validated_data.pop('device_id')
        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
            validated_data['device'] = device
            
            # Update device last_seen
            from django.utils import timezone
            device.last_seen = timezone.now()
            device.save(update_fields=['last_seen'])
            
            return super().create(validated_data)
        except Device.DoesNotExist:
            raise serializers.ValidationError({'device_id': 'Device not found or inactive'})


class AlertSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'device', 'device_name', 'alert_type', 'severity', 'message',
                 'timestamp', 'is_resolved', 'resolved_at', 'resolved_by_username',
                 'threshold_value', 'actual_value']
        read_only_fields = ['id', 'timestamp']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'phone_number', 'address', 'email_notifications', 
                 'sms_notifications', 'billing_cycle']


class BillSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    
    class Meta:
        model = Bill
        fields = ['id', 'user', 'device', 'start_date', 'end_date', 
                 'total_consumption', 'total_cost', 'is_paid', 'generated_at', 
                 'due_date', 'paid_at']
        read_only_fields = ['id', 'generated_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_devices = serializers.IntegerField()
    active_devices = serializers.IntegerField()
    total_consumption_today = serializers.FloatField()
    total_consumption_month = serializers.FloatField()
    active_alerts = serializers.IntegerField()
    monthly_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Recent readings
    latest_readings = WaterUsageSerializer(many=True)
    recent_alerts = AlertSerializer(many=True)

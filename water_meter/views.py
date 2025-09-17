from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Device, WaterUsage, Alert, UserProfile, Bill
from .serializers import (
    DeviceSerializer, WaterUsageSerializer, WaterUsageCreateSerializer,
    AlertSerializer, UserProfileSerializer, BillSerializer, DashboardStatsSerializer
)
from .authentication import DeviceAPIKeyAuthentication


class WaterUsageCreateView(generics.CreateAPIView):
    """API endpoint for IoT devices to submit water usage data"""
    serializer_class = WaterUsageCreateSerializer
    authentication_classes = [DeviceAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Get the device from authentication
        device = self.request.auth
        instance = serializer.save()
        
        # Log successful data save
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Water usage data saved for device {device.device_id}: "
                   f"Flow: {instance.flow_rate}L/min, Total: {instance.total_consumption}L")
        
        # Check for alerts after saving the data
        self.check_for_alerts(device, instance)
    
    def create(self, request, *args, **kwargs):
        """Override create to add better error handling and logging"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Received IoT data: {request.data}")
            response = super().create(request, *args, **kwargs)
            logger.info(f"Successfully processed IoT data from device")
            return response
        except Exception as e:
            logger.error(f"Error processing IoT data: {str(e)}")
            return Response(
                {'error': 'Failed to process data', 'details': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def check_for_alerts(self, device, usage):
        """Check for leak detection and excessive usage alerts"""
        from django.conf import settings
        
        # Check for leak (continuous flow for extended period)
        recent_readings = WaterUsage.objects.filter(
            device=device,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).order_by('-timestamp')[:6]  # Last 6 readings (1 hour of data)
        
        if len(recent_readings) >= 6:
            avg_flow = sum(r.flow_rate for r in recent_readings) / len(recent_readings)
            if avg_flow > settings.LEAK_THRESHOLD_LITERS_PER_HOUR / 60:  # Convert to per minute
                Alert.objects.get_or_create(
                    device=device,
                    alert_type='leak',
                    is_resolved=False,
                    defaults={
                        'severity': 'high',
                        'message': f'Potential leak detected. Continuous flow of {avg_flow:.2f} L/min for over 1 hour.',
                        'threshold_value': settings.LEAK_THRESHOLD_LITERS_PER_HOUR / 60,
                        'actual_value': avg_flow
                    }
                )
        
        # Check for excessive daily usage
        today = timezone.now().date()
        daily_usage = WaterUsage.objects.filter(
            device=device,
            timestamp__date=today
        ).aggregate(total=Sum('total_consumption'))['total'] or 0
        
        if daily_usage > settings.EXCESSIVE_USAGE_THRESHOLD_LITERS_PER_DAY:
            Alert.objects.get_or_create(
                device=device,
                alert_type='excessive',
                is_resolved=False,
                defaults={
                    'severity': 'medium',
                    'message': f'Excessive water usage detected. Daily consumption: {daily_usage:.2f} liters.',
                    'threshold_value': settings.EXCESSIVE_USAGE_THRESHOLD_LITERS_PER_DAY,
                    'actual_value': daily_usage
                }
            )


class WaterUsageListView(generics.ListAPIView):
    """API endpoint to retrieve water usage data"""
    serializer_class = WaterUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = WaterUsage.objects.select_related('device')
        
        # Filter by user's devices
        if not self.request.user.is_staff:
            queryset = queryset.filter(device__owner=self.request.user)
        
        # Filter by device
        device_id = self.request.query_params.get('device_id')
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        
        return queryset.order_by('-timestamp')


class DeviceListView(generics.ListAPIView):
    """API endpoint to list user's devices"""
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Device.objects.all()
        return Device.objects.filter(owner=self.request.user)


class AlertListView(generics.ListAPIView):
    """API endpoint to list alerts"""
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Alert.objects.select_related('device')
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(device__owner=self.request.user)
        
        # Filter by resolved status
        resolved = self.request.query_params.get('resolved')
        if resolved is not None:
            queryset = queryset.filter(is_resolved=resolved.lower() == 'true')
        
        return queryset.order_by('-timestamp')


class DashboardStatsView(APIView):
    """API endpoint for dashboard statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get user's devices
        devices = Device.objects.filter(owner=user) if not user.is_staff else Device.objects.all()
        
        # Calculate statistics
        total_devices = devices.count()
        active_devices = devices.filter(is_active=True).count()
        
        # Today's consumption
        today = timezone.now().date()
        today_usage = WaterUsage.objects.filter(
            device__in=devices,
            timestamp__date=today
        ).aggregate(total=Sum('total_consumption'))['total'] or 0
        
        # This month's consumption
        month_start = today.replace(day=1)
        month_usage = WaterUsage.objects.filter(
            device__in=devices,
            timestamp__date__gte=month_start
        ).aggregate(total=Sum('total_consumption'))['total'] or 0
        
        # Active alerts
        active_alerts = Alert.objects.filter(
            device__in=devices,
            is_resolved=False
        ).count()
        
        # Monthly cost
        from django.conf import settings
        monthly_cost = month_usage * settings.WATER_RATE_PER_LITER
        
        # Latest readings
        latest_readings = WaterUsage.objects.filter(
            device__in=devices
        ).select_related('device').order_by('-timestamp')[:10]
        
        # Recent alerts
        recent_alerts = Alert.objects.filter(
            device__in=devices
        ).select_related('device').order_by('-timestamp')[:5]
        
        data = {
            'total_devices': total_devices,
            'active_devices': active_devices,
            'total_consumption_today': today_usage,
            'total_consumption_month': month_usage,
            'active_alerts': active_alerts,
            'monthly_cost': monthly_cost,
            'latest_readings': WaterUsageSerializer(latest_readings, many=True).data,
            'recent_alerts': AlertSerializer(recent_alerts, many=True).data
        }
        
        return Response(data)


# Frontend Views
@login_required
def dashboard(request):
    """Main dashboard view"""
    return render(request, 'water_meter/dashboard.html')


@login_required
def devices(request):
    """Devices management view"""
    return render(request, 'water_meter/devices.html')


@login_required
def analytics(request):
    """Analytics and charts view"""
    return render(request, 'water_meter/analytics.html')


@login_required
def alerts(request):
    """Alerts management view"""
    return render(request, 'water_meter/alerts.html')


@login_required
def billing(request):
    """Billing and usage reports view"""
    return render(request, 'water_meter/billing.html')


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard')
    return render(request, 'water_meter/home.html')

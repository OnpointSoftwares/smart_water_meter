from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from .models import Device


class DeviceAPIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication for IoT devices using API keys
    """
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        
        try:
            device = Device.objects.get(api_key=api_key, is_active=True)
            # Return a tuple of (user, auth) where user is the device owner
            return (device.owner, device)
        except Device.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
    
    def authenticate_header(self, request):
        return 'X-API-Key'

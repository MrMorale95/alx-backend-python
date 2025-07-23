# myapp/middleware.py
from datetime import datetime, time
import logging
import os
from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.cache import cache
from datetime import timedelta

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        self.log_file = os.path.join(settings.BASE_DIR, 'requests.log')
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def __call__(self, request):
        # Get the user (or 'Anonymous' if not authenticated)
        user = request.user.username if request.user.is_authenticated else "Anonymous"
        logger.error(user)
        
        # Create log message
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')
        
        # Continue processing the request
        response = self.get_response(request)
        return response
    

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define restricted hours (9PM to 6AM)
        self.restricted_start = time(21, 0)  # 9 PM
        self.restricted_end = time(6, 0)    # 6 AM

    def __call__(self, request):
        from datetime import datetime
        
        current_time = datetime.now().time()
        
        # Check if current time is within restricted hours
        if (current_time >= self.restricted_start or 
            current_time <= self.restricted_end):
            
            # Allow access to admin even during restricted hours
            if not (request.user.is_authenticated and request.user.is_staff):
                return HttpResponseForbidden(
                    "<h1>Access Denied</h1>"
                    "<p>Messaging is only available between 6:00 AM and 9:00 PM</p>"
                )
        
        return self.get_response(request)
    

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limit configuration
        self.RATE_LIMIT = 5  # 5 messages
        self.TIME_WINDOW = 60  # 60 seconds (1 minute)
        self.BLOCK_DURATION = 300  # 5 minutes block if limit exceeded

    def __call__(self, request):
        # Only check POST requests to messaging endpoints
        if request.method == 'POST' and self.is_messaging_endpoint(request.path):
            ip_address = self.get_client_ip(request)
            
            # Check if IP is temporarily blocked
            if self.is_ip_blocked(ip_address):
                return self.too_many_requests_response()
                
            # Track message count
            if not self.allow_request(ip_address):
                # Block IP for exceeding rate limit
                self.block_ip(ip_address)
                return self.too_many_requests_response()
        
        return self.get_response(request)

    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    def is_messaging_endpoint(self, path):
        """Check if request is to a messaging endpoint"""
        return any(p in path for p in ['/send/', '/message/', '/chat/'])

    def allow_request(self, ip_address):
        """Check if request is within rate limits"""
        cache_key = f'message_count_{ip_address}'
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.RATE_LIMIT:
            return False
            
        cache.set(
            cache_key,
            current_count + 1,
            self.TIME_WINDOW
        )
        return True

    def is_ip_blocked(self, ip_address):
        """Check if IP is temporarily blocked"""
        return cache.get(f'blocked_{ip_address}', False)

    def block_ip(self, ip_address):
        """Block IP for exceeding rate limit"""
        cache.set(
            f'blocked_{ip_address}',
            True,
            self.BLOCK_DURATION
        )

    def too_many_requests_response(self):
        """Return 429 Too Many Requests response"""
        return HttpResponseForbidden(
            "Too many messages sent. Please wait before sending more.",
            status=429
        )    
    
class RolepermissionMiddleware :
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip permission check for these paths
        if request.path in ['/login/', '/admin/', '/static/']:
            return self.get_response(request)
            
        # Check if user has required role
        if not self.has_permission(request):
            return HttpResponseForbidden(
                "Access Denied: You don't have permission to access this resource",
                status=403
            )
        
        return self.get_response(request)

    def has_permission(self, request):
        """Check if user is admin or moderator"""
        if not request.user.is_authenticated:
            return False
            
        # Assuming you have 'is_moderator' field or similar in your User model
        return request.user.is_staff or request.user.is_moderator    
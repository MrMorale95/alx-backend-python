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
    

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuration
        self.limit = 5  # 5 messages
        self.window = 60  # 60 seconds = 1 minute

    def __call__(self, request):
        # Only process POST requests to message endpoints
        if request.method == 'POST' and any(path in request.path for path in ['/chat/', '/message/']):
            ip_address = self.get_client_ip(request)
            cache_key = f'rate_limit_{ip_address}'
            
            # Get current count
            current_count = cache.get(cache_key, 0)
            
            if current_count >= self.limit:
                return HttpResponseForbidden(
                    "Message limit exceeded. Please wait before sending more messages.",
                    status=429
                )
            
            # Increment count
            cache.set(
                cache_key,
                current_count + 1,
                self.window  # Automatically expires after window
            )
        
        return self.get_response(request)

    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip    
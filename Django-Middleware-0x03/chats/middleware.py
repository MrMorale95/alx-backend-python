# myapp/middleware.py
from datetime import datetime
import logging
import os
from django.conf import settings

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
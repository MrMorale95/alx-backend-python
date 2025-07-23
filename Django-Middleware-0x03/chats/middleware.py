from datetime import datetime
from django.http import HttpResponseForbidden
import time

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        with open('requests.log', 'a') as f:
            f.write(f"{datetime.now()} - User: {user} - Path: {request.path}\n")
        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        if now.hour >= 21 or now.hour < 6:
            return HttpResponseForbidden("Access restricted during this time.")
        response = self.get_response(request)
        return response

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}

    def __call__(self, request):
        if request.method == 'POST':
            ip_address = request.META.get('REMOTE_ADDR')
            if ip_address:
                current_time = time.time()
                request_history = self.requests.get(ip_address, [])
                one_minute_ago = current_time - 60
                recent_requests = [t for t in request_history if t > one_minute_ago]
                if len(recent_requests) >= 5:
                    return HttpResponseForbidden("Rate limit exceeded. You can send up to 5 messages per minute.")
                recent_requests.append(current_time)
                self.requests[ip_address] = recent_requests
        return self.get_response(request)

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.role not in ['admin', 'moderator']:
                return HttpResponseForbidden("You do not have permission to perform this action.")
        return self.get_response(request)
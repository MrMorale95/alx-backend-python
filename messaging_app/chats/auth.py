# chats/auth.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    # Extend or customize if needed (e.g., logging)
    pass

class CustomSessionAuthentication(SessionAuthentication):
    # Extend if needed
    pass
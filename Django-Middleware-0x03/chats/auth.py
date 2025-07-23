from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status

class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                samesite='Strict'
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                samesite='Strict'
            )
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access')
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                samesite='Strict'
            )
        return response

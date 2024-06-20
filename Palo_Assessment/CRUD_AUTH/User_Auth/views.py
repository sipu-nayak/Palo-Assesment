from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
import requests
from django.conf import settings

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_auth0_token(self):
        token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
        payload = {
            'grant_type': 'client_credentials',
            'client_id': settings.AUTH0_CLIENT_ID,
            'client_secret': settings.AUTH0_CLIENT_SECRET,
            'audience': f'https://{settings.AUTH0_DOMAIN}/api/v2/'
        }
        response = requests.post(token_url, json=payload)
        return response.json()['access_token']

    def get_auth_headers(self):
        return {
            'Authorization': f'Bearer {self.get_auth0_token()}',
            'Content-Type': 'application/json'
        }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = requests.post(
            f'https://{settings.AUTH0_DOMAIN}/api/v2/users',
            headers=self.get_auth_headers(),
            json=request.data
        )
        return Response(response.json(), status=response.status_code)

class UserDetailView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'auth0_id'

    def get_object(self):
        auth0_id = self.kwargs['auth0_id']
        response = requests.get(
            f'https://{settings.AUTH0_DOMAIN}/api/v2/users/{auth0_id}',
            headers=self.get_auth_headers()
        )
        response_data = response.json()
        return User(auth0_id=response_data['user_id'], name=response_data['name'], email=response_data['email'])

    def delete(self, request, *args, **kwargs):
        auth0_id = kwargs['auth0_id']
        response = requests.delete(
            f'https://{settings.AUTH0_DOMAIN}/api/v2/users/{auth0_id}',
            headers=self.get_auth_headers()
        )
        return Response(response.json(), status=response.status_code)




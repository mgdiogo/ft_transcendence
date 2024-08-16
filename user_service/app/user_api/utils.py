import os
import requests

JWT_API_URL = os.getenv('JWT_API_URL')

def request_jwt_api(path, method='post', data=None, headers=None):
    url = f'{JWT_API_URL}/{path}'
    response = requests.request(method, url, json=data, headers=headers)
    return response.json(), response.status_code

def create_token(username):
    data = {'username': username}
    return request_jwt_api('create/', data=data)

def validate_token(token):
    headers = {'Authorization': f'Bearer {token}'}
    request_jwt_api ('validate/', headers=headers)

def invalidate_token(token):
    headers = {'Authorization': f'Bearer {token}'}
    request_jwt_api ('validate/', headers=headers)
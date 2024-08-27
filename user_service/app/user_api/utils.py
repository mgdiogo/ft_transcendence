import os
import requests

JWT_API_URL = os.getenv('JWT_API_URL')


def request_jwt_api(path, method='POST', data=None, headers=None):
    url = f'{JWT_API_URL}/{path}'
    try:
        response = requests.request(method, url, json=data, headers=headers)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


def create_token(username):
    data = {'username': username}
    return request_jwt_api('create/', data=data)


def validate_token(token):
    headers = {'Authorization': f'Bearer {token}'}
    return request_jwt_api('validate/', headers=headers)


def invalidate_token(token):
    headers = {'Authorization': f'Bearer {token}'}
    return request_jwt_api('invalidate/', headers=headers)

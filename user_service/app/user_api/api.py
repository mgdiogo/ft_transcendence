import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.hashers import make_password, check_password
from .shared_models.models import User
from .utils import create_token, validate_token, invalidate_token

VALID_FIELDS = os.getenv('VALID_FIELDS').split(',')


def extract_token(request):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split('Bearer ')[-1].strip()
    return None


def validate_fields(data):
    invalid_fields = [
        field for field in data.keys() if field not in VALID_FIELDS]
    return invalid_fields


def jwt_auth(view_func):
    def wrapper(request, *args, **kwargs):
        token = extract_token(request)
        if not token:
            return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)
        
        response_data, status_code = validate_token(token)
        if status_code != 200:
            return JsonResponse({'error': response_data.get('error', 'Token validation failed')}, status=status_code)
        request.user_id = response_data['user_id']
        return view_func(request, *args, **kwargs)
    return wrapper


@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            invalid_fields = validate_fields(data)
            if invalid_fields:
                return JsonResponse({'error': f'Invalid fields: {", ".join(invalid_fields)}'}, status=400)
            if not data['name'] or not data['email'] or not data['password'] or not data['username']:
                return JsonResponse({'error': 'Name, email, password and username are required'}, status=400)

            user = User(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),
                username=data['username']
            )
            user.save()

            token_data, status_code = create_token(data['username'])
            if status_code != 201:
                return JsonResponse({'error': token_data.get('error', 'Token creation failed')}, status=status_code)
            return JsonResponse({'token': token_data['token']}, status=201)
        except Exception as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
@jwt_auth
def read_all(request):
    if request.method == 'GET':
        try:
            users = User.objects.all()
            data = {
                'users': list(users.values('id', 'name', 'email', 'username'))
            }
            return JsonResponse(data, status=200)
        except Exception as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
@jwt_auth
def read_user(request, user_id):
    if request.method == 'GET':
        try:
            id = int(user_id)
            user = User.objects.get(id=id)
            data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'username': user.username,
            }
            return JsonResponse(data, status=200)
        except ValueError:
            return JsonResponse({'error': 'Invalid user ID'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
@jwt_auth
def update_user(request, user_id):
    if request.method == 'PUT':
        try:
            user_id = int(user_id)
            data = json.loads(request.body)
            invalid_fields = validate_fields(data)
            if invalid_fields:
                return JsonResponse({'error': f'Invalid fields: {", ".join(invalid_fields)}'}, status=400)
            user = User.objects.get(id=user_id)
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            if 'password' in data:
                user.password = make_password(data['password'])
            user.username = data.get('username', user.username)
            user.save()
            return JsonResponse({'message': 'User updated sucessfully!'}, status=200)
        except ValueError:
            return JsonResponse({'error': 'Invalid user ID'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
@jwt_auth
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user_id = int(user_id)
            token = extract_token(request)
            if token:
                invalidate_token(token)
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'message': 'User deleted sucessfully!'}, status=200)
        except ValueError:
            return JsonResponse({'error': 'Invalid user ID'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
def auth_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            invalid_fields = validate_fields(data)
            if invalid_fields:
                return JsonResponse({'error': f'Invalid fields: {", ".join(invalid_fields)}'}, status=400)
            username = data.get('username', '')
            password = data.get('password', '')

            user = User.objects.get(username=username)
            if user.check_password(password):
                token_data, status_code = create_token(data['username'])
                if status_code != 201:
                    return JsonResponse({'error': token_data.get('error', 'Token creation failed')}, status=status_code)
                return JsonResponse({'token': token_data['token']}, status=201)
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=401)
        except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid username or password'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
def logout_user(request):
    if request.method == 'POST':
        try:
            token = extract_token(request)
            if token:
                invalidate_token(token)
                return JsonResponse({'message': 'Logout successful'}, status=200)
            else:
                return JsonResponse({'error': 'Missing token'}, status=401)
        except Exception as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
    return HttpResponseBadRequest('Invalid method')

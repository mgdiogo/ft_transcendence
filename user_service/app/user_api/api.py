import os
import json
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.hashers import make_password, check_password
from .models import User, TokenBlacklist
from .utils import generate_jwt, decode_jwt

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
    @csrf_exempt
    def wrapper(request, *args, **kwargs):
        token = extract_token(request)
        if not token:
            return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)
        try:
            payload = decode_jwt(token)
            if datetime.now().timestamp() > payload['exp']:
                return JsonResponse({'error': 'Token expired'}, status=401)
            request.user_id = payload['user_id']
            return view_func(request, *args, **kwargs)
        except ValueError as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
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

            token = generate_jwt({
                'user_id': user.id,
                'exp': (datetime.now() + timedelta(days=1)).timestamp()
            })

            return JsonResponse({'token': token}, status=201)
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
            try:
                id = int(user_id)
            except ValueError:
                return JsonResponse({'error': 'Invalid user ID'}, status=400)
            user = User.objects.get(id=id)
            data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'username': user.username,
            }
            return JsonResponse(data, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
@jwt_auth
def update_user(request, user_id):
    if request.method == 'PUT':
        try:
            user_id = int(user_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid user ID'}, status=400)

        try:
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
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
@jwt_auth
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user_id = int(user_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid user ID'}, status=400)

        try:
            token = extract_token(request)
            if token:
                payload = decode_jwt(token)
                if datetime.fromtimestamp(payload['exp']) > datetime.now():
                    TokenBlacklist.objects.create(token=token)
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'message': 'User deleted sucessfully!'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
def auth_user(request):
    if request.method == 'POST':
        try:
            token = extract_token(request)
            data = json.loads(request.body)
            invalid_fields = validate_fields(data)
            if invalid_fields:
                return JsonResponse({'error': f'Invalid fields: {", ".join(invalid_fields)}'}, status=400)
            username = data.get('username', '')
            password = data.get('password', '')

            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password) is False:
                    raise User.DoesNotExist
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

            if token:
                try:
                    payload = decode_jwt(token)
                    expired = datetime.fromtimestamp(
                        payload['exp']) <= datetime.now()
                    blacklisted = TokenBlacklist.objects.filter(
                        token=token).exists()

                    if not expired and not blacklisted:
                        return JsonResponse({'token': token}, status=200)
                except ValueError as e:
                    pass

                token = generate_jwt({
                    'user_id': user.id,
                    'exp': (datetime.now() + timedelta(days=1)).timestamp()
                })
                return JsonResponse({'token': token}, status=200)
            return JsonResponse({'error': 'Missing token or invalid format'}, status=401)
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
                payload = decode_jwt(token)
                if datetime.fromtimestamp(payload['exp']) > datetime.now():
                    TokenBlacklist.objects.create(token=token)
                return JsonResponse({'message': 'Logout successful'}, status=200)
            else:
                return JsonResponse({'error': 'Missing token'}, status=401)
        except Exception as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
    return HttpResponseBadRequest('Invalid method')

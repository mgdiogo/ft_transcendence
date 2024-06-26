from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from .utils import generate_jwt, decode_jwt
from datetime import datetime, timedelta
import json


def jwt_auth(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)

        token = auth_header.split('Bearer ')[1]
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


@jwt_auth
def read_user(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=user_id)
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


@jwt_auth
def update_user(request, user_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
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


@jwt_auth
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
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
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)
            
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            
            if check_password(password, user.password):
                token = request.headers.get('Authorization', '')
                if token:
                    try:
                        payload = decode_jwt(token)
                        if datetime.fromtimestamp(payload['exp']) > datetime.now():
                            return JsonResponse({'token': token}, status=200)
                    except ValueError:
                        pass
                
                token = generate_jwt({
                    'user_id': user.id,
                    'exp': (datetime.now() + timedelta(days=1)).timestamp()
                })
                return JsonResponse({'token': token}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
    return HttpResponseBadRequest('Invalid method')

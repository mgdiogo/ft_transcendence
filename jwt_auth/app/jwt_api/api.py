import json
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import User, TokenBlacklist
from .utils import generate_jwt, decode_jwt


def extract_token(request):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split('Bearer ')[-1].strip()
    return None


@csrf_exempt
def validate_token(request):
    if request.method == 'POST':
        try:
            token = extract_token(request)
            if not token:
                return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)

            payload = decode_jwt(token)
            if datetime.now().timestamp() > payload['exp']:
                return JsonResponse({'error': 'Token expired'}, status=401)
            if TokenBlacklist.objects.filter(token=token).exists():
                return JsonResponse({'error': 'Token blacklisted'}, status=401)

            return JsonResponse({'valid': True, 'user_id': payload['user_id']}, status=200)
        except ValueError:
            return JsonResponse({'error': 'Invalid token'}, status=400)
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
def create_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user = User.objects.get(username=username)
            token = generate_jwt({
                'user_id': user.id,
                'exp': (datetime.now() + timedelta(days=1)).timestamp()
            })
            return JsonResponse({'token': token}, status=201)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid username'}, status=400)
        except Exception as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
    return HttpResponseBadRequest('Invalid method')


@csrf_exempt
def invalidate_token(request):
    if request.method == 'POST':
        try:
            token = extract_token(request)
            if not token:
                return JsonResponse({'error': 'Missing token'}, status=401)

            TokenBlacklist.objects.create(token=token)
            return JsonResponse({'message': 'Token invalidated'}, status=200)
        except Exception as e:
            return HttpResponseBadRequest(f'Error: {str(e)}')
    return HttpResponseBadRequest('Invalid method')

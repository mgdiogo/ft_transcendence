from django.urls import path
from . import api

urlpatterns = [
    path('create/', api.create_token, name='create_token'),
    path('validate/', api.validate_token, name='validate_token'),
    path('invalidate/', api.invalidate_token, name='invalidate_token'),
]
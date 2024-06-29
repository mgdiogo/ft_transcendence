from django.urls import path
from . import api

urlpatterns = [
    path('create/', api.create_user, name='create_user'),
    path('read/', api.read_all, name='read_all'),
    path('read/<int:user_id>/', api.read_user, name='read_user'),
    path('update/<int:user_id>/', api.update_user, name='update_user'),
    path('delete/<int:user_id>/', api.delete_user, name='delete_user'),
    path('auth/', api.auth_user, name='auth_user'),
    path('logout/', api.logout_user, name='logout_user'),
]

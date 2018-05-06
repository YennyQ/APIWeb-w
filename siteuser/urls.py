"""
用户模块路由映射
"""
from django.urls import path, include
from siteuser.views import (
    register_user,
    login_user,
    logout_user,
    send_confirm_mail,
    confirm_user,
    send_reset_mail,
    password_reset,
    password_change,
    api_root,
    UserListView,
    UserListViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', UserListViewSet)

urlpatterns = [
    path('', api_root),
    path('', include(router.urls)),

    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    path('send_confirm_mail/', send_confirm_mail, name='send_confirm_mail'),
    path('confirm/<str:token>', confirm_user, name='confirm'),

    path('send_reset_mail/', send_reset_mail, name='send_reset_mail'),
    path('password_reset/<str:token>', password_reset, name='password_reset'),

    path('password_change/', password_change, name='password_change'),
]

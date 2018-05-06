"""
用户模块路由
"""
from utils.functions import log
from rest_framework.reverse import reverse

from rest_framework.decorators import api_view
from rest_framework import (
    generics,
    mixins,
    views,
    viewsets,
    filters,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from siteuser.serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    SendResetMailSerializer,
    PasswordResetSerializer,
    PasswordChangeSerializer,
)
from rest_framework.response import Response
from utils.response import (
    SuccessResponse,
    CreatedResponse,
    ErrorResponse,
)
from django.contrib.auth import (
    get_user_model,
    authenticate,
    login,
    logout,
)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

APIView = views.APIView

User = get_user_model()

class UserPagination(PageNumberPagination):
    """
    针对view单独定制分页相关
    """
    page_size = 1
    page_size_query_param = 'ps'
    page_query_param = 'p'


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination


class UserListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filers.OrderingFilter)
    # DjangoFilterBackend过滤器，此处为精确匹配，
    # 也可查看官方filter文档做自定义某个model的filterclass，
    # 比如查找区间，或模糊查询，自定义的filterclass要自行加filter_class属性=(自定义class)，
    # 此时就不需要再在此处加这个fileds了
    filter_fields = ('id', 'username')   # 自定义时filter_class顶替fields
    # filters.SearchFilter DRF的模糊查询，search精确到某个字段的各自搜索级别，搜索多个
    search_fields = ('^username', 'email')
    # filers.OrderingFilter DRF的排序功能
    ordering_fields = ('id', 'last_login')


    # 和queryset留其一即可
    # def get_queryset(self):
    #     # 此句不会产生查询
    #     queryset = User.objects.all()
    #     p_min = self.request.query_paramas,get('p_min', 0)
    #     if p_min:
    #         queryset = queryset.filter()
    #     return queryset


class RegisterAPIView(APIView):
    """
    用户注册路由
    """
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        url_name = 'confirm'
        subject = 'Confirm Email'
        message = 'confirm your email address'
        user.send_mail_with_url(request, url_name, subject, message)
        return CreatedResponse(serializer.data)


class SendConfirmMailAPIView(APIView):
    """
    发送邮箱验证邮件
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        url_name = 'confirm'
        subject = 'Confirm Email'
        message = 'confirm your email address'
        user.send_mail_with_url(request, url_name, subject, message)
        return SuccessResponse()


class ComfirmAPIView(APIView):
    """
    邮件验证路由
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, token):
        user = request.user
        is_confirmed = user.confirm(token)
        if not is_confirmed:
            data = {'detail': 'token错误或失效'}
            return ErrorResponse(data)
        return SuccessResponse()


class LoginAPIView(APIView):
    """
    用户登录路由
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if not user:
            data = {'detail': '登录失败'}
            return ErrorResponse(data)
        login(request=request, user=user)
        return SuccessResponse()


class LogoutAPIView(APIView):
    """
    用户登出路由
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        logout(request=request)
        return SuccessResponse()


class SendResetMailAPI(APIView):
    """
    忘记密码，发送确认邮件
    """
    permission_classes = (AllowAny,)
    serializer_class = SendResetMailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer中的validate确保了该username的用户一定存在，故可直接get
        user = User.objects.get(username=serializer.data.get('username'))
        url_name = 'password_reset'
        subject = 'Reset Password'
        message = 'reset your password'
        user.send_mail_with_url(request, url_name, subject, message)
        return SuccessResponse()


class PasswordResetAPIView(APIView):
    """
    忘记密码重置
    """
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def post(self, request, token):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user_from_token(token)
        if not user:
            data = {'detail': 'token错误或失效'}
            return ErrorResponse(data)
        serializer.update(user, data)
        return SuccessResponse()


class PasswordChangeAPIView(APIView):
    """
    用户修改密码路由
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not serializer.check(user, data):
            data = {'detail': '原密码错误'}
            return ErrorResponse(data)
        serializer.update(user, data)
        return SuccessResponse()


@api_view(['GET'])
def api_root(request, format=None):
    """
    链接URL的根链接
    """
    return Response({
        # 'users': reverse('user-list', request=request, format=format),
        'register_user': reverse(register_user, request=request, format=format),
        'login_user': reverse(login_user, request=request, format=format),
        'logout_user': reverse(logout_user, request=request, format=format),
        'send_confirm_mail': reverse(send_confirm_mail, request=request, format=format),
        'send_reset_mail': reverse(send_reset_mail, request=request, format=format),
        'password_change': reverse(password_change, request=request, format=format),

    })

# todo: 动态路由是否能添加到根链接中展示
# 'confirm/<str:token>': reverse(confirm_user, kwargs={'token': '1'}, request=request, format=format),
# 'password_reset/<str:token>': reverse(password_reset, kwargs={'token': '1'}, request=request, format=format),


register_user = RegisterAPIView.as_view()
login_user = LoginAPIView.as_view()
logout_user = LogoutAPIView.as_view()
send_confirm_mail = SendConfirmMailAPIView.as_view()
confirm_user = ComfirmAPIView.as_view()
send_reset_mail = SendResetMailAPI.as_view()
password_reset = PasswordResetAPIView.as_view()
password_change = PasswordChangeAPIView.as_view()
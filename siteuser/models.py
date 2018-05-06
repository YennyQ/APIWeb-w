"""
用户模块数据表
"""
from utils.functions import (
    log,
    datetime_to_timestamp,
)
from utils.base_model import SiteBaseModel
from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from threading import Thread
import jwt
from datetime import (
    datetime,
    timedelta,
)
from django.conf import settings
from rest_framework.reverse import reverse

FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
SECRET_KEY = settings.SECRET_KEY


class User(AbstractUser):
    """
    用户数据表
    """

    is_confirmed = models.BooleanField(_('email confirm'), default=False)
    company = models.ForeignKey(
        'Company',
        models.SET_NULL,
        blank=True,
        null=True,
    )


    def _generate_jwt_token(self, seconds):
        """
        生成过期时间为seconds秒的token
        """
        dt = datetime.now() + timedelta(seconds=seconds)
        exp = datetime_to_timestamp(dt)
        token = jwt.encode({
            'id': self.pk,
            'exp': exp
        }, SECRET_KEY)
        return token.decode('utf-8')

    @property
    def token(self):
        seconds = 60 * 60
        return self._generate_jwt_token(seconds)

    def send_mail(self, subject, message):
        """
        发送邮件
        """
        thr = Thread(
            target=send_mail,
            args=[
                subject,
                message,
                FROM_EMAIL,
                [self.email],
                {'fail_silently': True},
            ]
        )
        thr.start()

    def send_mail_with_url(self, request, url_name, subject, message):
        relative_url = reverse(url_name, kwargs={'token': self.token})
        url = request.build_absolute_uri(relative_url)
        self.send_mail(subject, '{message} url \n{url}'.format(message=message, url=url))

    @staticmethod
    def decode_token(token):
        """
        解码token中的原始数据
        """
        try:
            data = jwt.decode((token.encode('utf-8')), SECRET_KEY)
        # jwt.exceptions.ExpiredSignatureError token过期
        except Exception:
            data = {}
        return data

    def confirm(self, token):
        """
        用户邮箱验证
        """
        if not self.is_confirmed:
            data = self.decode_token(token)
            if data.get('id') != self.id:
                return False
            self.is_confirmed = True
            self.save()
            return True
        return True


class Company(SiteBaseModel):
    """
    公司信息表
    """

    name = models.CharField(
        _('company name'),
        max_length=150,
        unique=True,
    )
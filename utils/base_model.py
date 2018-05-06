"""
基础model
"""
from django.db import models


class SiteBaseModel(models.Model):
    ct = models.DateTimeField('创建时间', auto_now_add=True)
    ut = models.DateTimeField('更新时间', auto_now=True)
    create_uid = models.IntegerField('创建者', null=True)
    update_uid = models.IntegerField('更新者', null=True)

    class Meta:
        abstract = True


# -*- coding: utf-8 -*-

from django.db import models


class AbstractWeChatUser(models.Model):
    unionid = models.CharField(max_length=32, verbose_name='UnionID')

    # unionid字段设置
    UNIONID_FIELD = 'unionid'
    # openid字段设置
    OPENID_PREFIX = 'openid'
    OPENID_PREFIX_SEPARATOR = '_'
    OPENID_CLIENT_LABELS = []  # 用以设置和生成openid字段

    class Meta:
        abstract = True


class WeChatUser(AbstractWeChatUser):
    class Meta:
        managed = False

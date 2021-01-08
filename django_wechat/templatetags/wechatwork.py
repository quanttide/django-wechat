# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.inclusion_tag('tags/django_wechat/wechat_login_native_qrcode.html')
def wechatwork_login_qrcode():
    """
    生成企业微信登录二维码
    :return:
    """
    pass

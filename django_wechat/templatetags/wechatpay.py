# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.inclusion_tag('tags/django_wechat/wechatpay_qrcode.html')
def wechatpay_qrcode(code_url):
    """
    生成微信支付二维码
    :return:
    """
    pass

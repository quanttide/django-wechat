# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.inclusion_tag('tags/django_wechat/wechat_login_native_qrcode.html')
def wechat_login_native_qrcode(appid, redirect_uri, state=None, self_redirect: bool = False, style='black', href=None):
    """
    生成微信Native登录二维码
    :param appid: 应用唯一标识。
    :param redirect_uri: 重定向地址。
    :param state: optional, 默认为None。用于保持请求和回调的状态，授权请求后原样带回给第三方；
    该参数可用于防止csrf攻击（跨站请求伪造攻击）；
    建议第三方带上该参数，可设置为简单的随机数加session进行校验。
    :param self_redirect: optional, 默认为False。
      - True：手机点击确认登录后可以在 iframe 内跳转到 redirect_uri
      - False：手机点击确认登录后可以在 top window 跳转到 redirect_uri
    :param style: optional, 默认为'black'。文字描述字体颜色。
      - 'black': 黑色字体，适合浅色背景
      - 'white': 白色字体，适合深色背景
    :param href: optional, 默认为None。自定义CSS样式链接，第三方可根据实际需求覆盖默认样式
    :return:
    """
    return {
        'appid': appid,
        'redirect_uri': redirect_uri,
        'state': state,
        'self_redirect': self_redirect,
        'style': style,
        'href': href,
    }

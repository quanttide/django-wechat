# -*- coding: utf-8 -*-
"""
微信登录服务端API
"""

from wechat_login_sdk import get_access_token, get_userinfo

from django_wechat.django_wechat_login.settings import wechat_login_sdk_settings


def get_wechat_access_token(code, app_label=None):
    """

    :param code: 客户端授权临时票据
    :param app_label: 开发者定义微信应用标签
    :return:
    """
    # 处理微信应用标签
    if app_label is None:
        app_label = 'default'
    else:
        assert app_label in wechat_login_sdk_settings.keys(), "微信应用标签不在开发者定义的范围内"

    # 微信应用配置
    wechat_app_settings = wechat_login_sdk_settings['app_label']
    # AppId和AppSecret
    appid = wechat_app_settings.get('APPID')
    app_secret = wechat_app_settings.get('APPSECRET')

    # 标记是否为小程序
    is_mp = (wechat_app_settings.get('TYPE') == 'MP')

    return get_access_token(appid, app_secret, code, is_mp)


def get_wechat_userinfo(openid, access_token):
    return get_userinfo(openid, access_token)

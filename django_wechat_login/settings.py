# -*- coding: utf-8 -*-

from django.conf import settings
from rest_framework.settings import APISettings


# 用户定义参数
#
# 传入格式示例：
# {
#   'default': {
#       'APPID': '<your_app_id>',
#       'APPSECRET': '<your_app_secret>',
#       'TYPE': '<type_defined_by_wechat>',
#   }
# }
#
# TYPE可选项：
#  - JSAPI（微信网页）
#  - APP（移动应用）
#  - H5（手机网页）
#  - Native（扫码）
#  - MP（小程序）
USER_SETTINGS = getattr(settings, 'WECHAT_LOGIN', None)

# 默认参数
DEFAULTS = {

}

# 字符串格式导入的模块
IMPORT_STRINGS = []

# settings实例
wechat_login_sdk_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)

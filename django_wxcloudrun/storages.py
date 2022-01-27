"""
微信云托管Django存储类，包括：
- 文件存储使用环境内对象存储，API见：https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/development/storage/service/。
- 静态文件存储使用环境内静态文件存储。

开发指南：https://docs.djangoproject.com/en/4.0/howto/custom-file-storage/。
"""
from abc import ABC

from django.core.files.storage import Storage


class WXCloudRunStorage(Storage, ABC):
    pass


class WXCloudRunStaticStorage(object):
    pass

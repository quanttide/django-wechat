"""
微信云托管Django应用设置

容器内环境变量：
  - https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/development/weixin/
"""

import os

# 当前环境ID
CBR_ENV_ID = os.environ.get('CBR_ENV_ID', None)

# 是否为微信云托管运行环境
# 微信云托管环境有环境ID，本地环境等非微信云托管环境无（手动传入除外）。
IS_WXCLOUDRUN_ENV = (CBR_ENV_ID is not None)

# MySQL数据库
# 仅在模板创建项目时生成，如果手动开通或非模板部署则不生成。
# 用户名
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', None)
# 密码
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', None)
# 内网地址
MYSQL_ADDRESS = os.environ.get('MYSQL_ADDRESS', None)

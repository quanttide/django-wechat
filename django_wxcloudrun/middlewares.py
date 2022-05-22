"""
微信云托管Django中间件
"""


class WXCloudRunMiddleware(object):
    def process_wxcloudrun_header(self, request):
        """
        处理微信云托管请求Header的微信信息

        详见：https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/development/weixin/

        :param request:
        :return:
        """
        return request

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

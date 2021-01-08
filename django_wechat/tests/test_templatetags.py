# -*- coding: utf-8 -*-


from django.test import TestCase
from django.template import Context, Template


class QrCodeTemplateTagTestCase(TestCase):
    def test_render_template_tag(self):
        """
        测试通过
        :return:
        """
        out = Template("""
        {% load wechat_login %}
        {% wechat_login_native_qrcode appid redirect_uri %}
        """).render(
            Context({
                "appid": "wxafdc40f7dce5daa5",
                "redirect_uri": "https://users.quanttidetech.com",
            })
        )
        self.assertTrue(out)
        print(out)

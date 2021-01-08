# -*- coding: utf-8 -*-
"""
企业微信SDK测试样例

测试记录：
- 2020-07-07 全部通过测试
"""

from django.test import TestCase
from django.utils import timezone

from ..sdk.work import *


class AccessTokenTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.corpid = CORPID
        cls.secret = CONTACT_SECRET

    def test_get_access_token(self):
        access_token, expire_in = get_access_token(self.corpid, self.secret)
        self.assertIsNotNone(access_token)
        self.assertEqual(expire_in, 7200)


class MsgDecryptTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        使用企业微信官方文档的demo数据为测试数据
        Refs:
            - https://work.weixin.qq.com/api/doc/90000/90139/90968
        :return:
        """
        cls.corpid = "wx5823bf96d3bd56c7"
        cls.token = "QDG6eK"
        cls.encoding_aes_key = "jWmYm7qr5nMoAUwZRjGtBxmz3KA1tkAj3ykkR6q2B2C"

        cls.sign = "477715d11cdb4164915debcba66cb864d751f3e6"
        cls.timestamp = "1409659813"
        cls.nonce = "1372623149"
        cls.nonce_16 = '0960688932c47ef1'

        cls.raw_msg_encrypt = """<xml>
            <ToUserName><![CDATA[wx5823bf96d3bd56c7]]></ToUserName><Encrypt><![CDATA[RypEvHKD8QQKFhvQ6QleEB4J58tiPdvo+rtK1I9qca6aM/wvqnLSV5zEPeusUiX5L5X/0lWfrf0QADHHhGd3QczcdCUpj911L3vg3W/sYYvuJTs3TUUkSUXxaccAS0qhxchrRYt66wiSpGLYL42aM6A8dTT+6k4aSknmPj48kzJs8qLjvd4Xgpue06DOdnLxAUHzM6+kDZ+HMZfJYuR+LtwGc2hgf5gsijff0ekUNXZiqATP7PF5mZxZ3Izoun1s4zG4LUMnvw2r+KqCKIw+3IQH03v+BCA9nMELNqbSf6tiWSrXJB3LAVGUcallcrw8V2t9EL4EhzJWrQUax5wLVMNS0+rUPA3k22Ncx4XXZS9o0MBH27Bo6BpNelZpS+/uh9KsNlY6bHCmJU9p8g7m3fVKn28H3KDYA5Pl/T8Z1ptDAVe0lXdQ2YoyyH2uyPIGHBZZIs2pDBS8R07+qN+E7Q==]]></Encrypt>
            <AgentID><![CDATA[218]]></AgentID>
            </xml>""".replace('\n', '').replace('\r', '').replace(' ','')
        cls.msg_encrypt = "RypEvHKD8QQKFhvQ6QleEB4J58tiPdvo+rtK1I9qca6aM/wvqnLSV5zEPeusUiX5L5X/0lWfrf0QADHHhGd3QczcdCUpj911L3vg3W/sYYvuJTs3TUUkSUXxaccAS0qhxchrRYt66wiSpGLYL42aM6A8dTT+6k4aSknmPj48kzJs8qLjvd4Xgpue06DOdnLxAUHzM6+kDZ+HMZfJYuR+LtwGc2hgf5gsijff0ekUNXZiqATP7PF5mZxZ3Izoun1s4zG4LUMnvw2r+KqCKIw+3IQH03v+BCA9nMELNqbSf6tiWSrXJB3LAVGUcallcrw8V2t9EL4EhzJWrQUax5wLVMNS0+rUPA3k22Ncx4XXZS9o0MBH27Bo6BpNelZpS+/uh9KsNlY6bHCmJU9p8g7m3fVKn28H3KDYA5Pl/T8Z1ptDAVe0lXdQ2YoyyH2uyPIGHBZZIs2pDBS8R07+qN+E7Q=="
        cls.random_msg = '0960688932c47ef1\x00\x00\x01\x1c<xml><ToUserName><![CDATA[wx5823bf96d3bd56c7]]></ToUserName>\n<FromUserName><![CDATA[mycreate]]></FromUserName>\n<CreateTime>1409659813</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[hello]]></Content>\n<MsgId>4561255354251345929</MsgId>\n<AgentID>218</AgentID>\n</xml>wx5823bf96d3bd56c7'
        cls.msg = """<xml><ToUserName><![CDATA[wx5823bf96d3bd56c7]]></ToUserName>
               <FromUserName><![CDATA[mycreate]]></FromUserName>
               <CreateTime>1409659813</CreateTime>
               <MsgType><![CDATA[text]]></MsgType>
               <Content><![CDATA[hello]]></Content>
               <MsgId>4561255354251345929</MsgId>
               <AgentID>218</AgentID>
               </xml>""".replace(' ', '')
        cls.data = xmltodict.parse(cls.msg)['xml']

        cls.pad_num = 30
        cls.xml_len = 284

    # ----- 解密测试 -----

    def test_aes_decrypt(self):
        random_msg = aes_decrypt(msg_encrypt=self.msg_encrypt, encoding_aes_key=self.encoding_aes_key)
        self.assertEqual(random_msg, self.random_msg)

    def test_decrypt_msg(self):
        data = decrypt_msg(self.raw_msg_encrypt, self.sign, self.timestamp, self.nonce, self.token, self.encoding_aes_key)
        self.assertEqual(data['ToUserName'], self.corpid)

    # ----- 加密测试 -----

    def test_gen_random_str(self):
        random_msg = gen_random_msg(self.data, random_str_16=self.nonce_16)
        self.assertEqual(random_msg, self.random_msg)

    def test_aes_encrypt(self):
        msg_encrypt = aes_encrypt(self.random_msg, self.encoding_aes_key)
        self.assertEqual(msg_encrypt, self.msg_encrypt)

    def test_gen_xml_text(self):
        xml_str = gen_xml_text(self.msg_encrypt, self.sign, self.timestamp, self.nonce)
        msg_encrypt = xmltodict.parse(xml_str)['xml']['Encrypt']
        self.assertEqual(msg_encrypt, self.msg_encrypt)

    def test_encrypt_msg(self):
        raw_msg_encrypt = encrypt_msg(data=self.data, token=self.token, encoding_aes_key=self.encoding_aes_key,
                                      timestamp=self.timestamp, nonce=self.nonce, random_str_16=self.nonce_16)
        msg_encrypt = xmltodict.parse(raw_msg_encrypt)['xml']['Encrypt']
        self.assertEqual(msg_encrypt, self.msg_encrypt)


class WeChatSDKTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sdk = WeChatWorkSDK(secret=CONTACT_SECRET)

    def test_get_access_token(self):
        access_token = self.sdk.access_token
        self.assertIsNotNone(access_token)


class UserSDKTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sdk = UserSDK()
        cls.test_user = {
            'userid': 'test_user',
            'name': 'test_user',
            'department': [1],
            'email': 'test@quanttide.com',
        }

    def _create(self):
        response = self.sdk.create(self.test_user)
        self.assertFalse('errcode' in response and response['errcode'] != 0)

    def _get(self):
        response = self.sdk.get(userid=self.test_user['userid'])
        self.assertFalse('errcode' in response and response['errcode'] != 0)
        self.assertEqual(response['name'], self.test_user['name'])

    def _update(self):
        self.test_user['name'] = 'updated'
        response = self.sdk.update(data=self.test_user)
        self.assertFalse('errcode' in response and response['errcode'] != 0)

    def _delete(self):
        response = self.sdk.delete(userid=self.test_user['userid'])
        self.assertFalse('errcode' in response and response['errcode'] != 0)

    def test_modify_user(self):
        """
        按照执行顺序编写测试，否则TestCase会按照字母排序等默认方式排序运行
        :return:
        """
        self._create()
        self._get()
        self._update()
        self._delete()

    def test_list(self):
        response = self.sdk.list()
        self.assertFalse('errcode' in response and response['errcode'] != 0)

    def test_get_active_stat(self):
        active_cnt = self.sdk.get_active_stat(date="2020-10-04")
        self.assertIsInstance(active_cnt, int)


class DepartmentSDKTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sdk = DepartmentSDK()

    def test_list(self):
        response = self.sdk.list()
        self.assertFalse('errcode' in response and response['errcode'] != 0)


class TagSDKTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sdk = TagSDK()

    def test_list(self):
        response = self.sdk.list()
        self.assertFalse('errcode' in response and response['errcode'] != 0)




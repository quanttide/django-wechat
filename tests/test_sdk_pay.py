# -*- coding: utf-8 -*-

from wechatpy.pay.utils import calculate_signature
from django.test import TestCase
from django.conf import settings

from django_wechat.sdk.pay import *


class ParseUnifiedOrderResultTestCase(TestCase):
    def test_parse_wechat_unifiedorder_result_native(self):
        pass


class QueryOrderTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client_label = 'qtclass_wxweb'
        cls.qt_order_id = 'qtorder_20200915182157105164'

    def test_query_wechatpay_order(self):
        result = query_wechatpay_order(self.client_label, out_trade_no=self.qt_order_id)
        self.assertTrue(result)
        print(result)


class NotifyOrderTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.raw_data = {
            'appid': settings.WECHAT_APP_SECRETS['qtclass_wxweb']['appid'],
            'attach': '支付测试',
            'bank_type': 'CFT',
            'fee_type': 'CNY',
            'is_subscribe': 'Y',
            'mch_id': MCH_ID,
            'nonce_str': '5d2b6c2a8db53831f7eda20af46e531c',
            'openid': 'o5UdX0hDXymhfKmk1whTVUlIwZqE',
            'out_trade_no': 'qtorder_20200915182157105164',
            'result_code': 'SUCCESS',
            'return_code': 'SUCCESS',
            'time_end': '20200915210540',
            'total_fee': '1',
            'trade_type': "JSAPI",
            'transaction_id': '4200000688202009159176613942',
        }
        cls.raw_data['sign'] = calculate_signature(params=cls.raw_data, api_key=MCH_API_KEY)
        cls.xml_raw_data = """
        <xml>
          <appid><![CDATA[{appid}]]></appid>
          <attach><![CDATA[{attach}]]></attach>
          <bank_type><![CDATA[{bank_type}]]></bank_type>
          <fee_type><![CDATA[{fee_type}]]></fee_type>
          <is_subscribe><![CDATA[{is_subscribe}]]></is_subscribe>
          <mch_id><![CDATA[{mch_id}]]></mch_id>
          <nonce_str><![CDATA[{nonce_str}]]></nonce_str>
          <openid><![CDATA[{openid}]]></openid>
          <out_trade_no><![CDATA[{out_trade_no}]]></out_trade_no>
          <result_code><![CDATA[{result_code}]]></result_code>
          <return_code><![CDATA[{return_code}]]></return_code>
          <sign><![CDATA[{sign}]]></sign>
          <time_end><![CDATA[{time_end}]]></time_end>
          <total_fee>{total_fee}</total_fee>
          <trade_type><![CDATA[{trade_type}]]></trade_type>
          <transaction_id><![CDATA[{transaction_id}]]></transaction_id>
        </xml>
        """.format(**cls.raw_data)

    def test_parse_wechatpay_notify_data(self):
        data = parse_wechatpay_notify_data(self.xml_raw_data)
        self.assertTrue(data)
        print(data)

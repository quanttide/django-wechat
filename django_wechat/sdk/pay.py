# -*- coding: utf-8 -*-

import time
from functools import partial

from django.conf import settings

from wechatpy.pay import WeChatPay
from wechatpy.pay.api import WeChatOrder
from wechatpy.pay.utils import calculate_signature


WECHAT_NOTIFY_URL = settings.WECHATPAY_NOTIFY_URL

MCH_API_KEY = settings.WECHATPAY_SECRETS['mch_api_key']
MCH_ID = settings.WECHATPAY_SECRETS['mch_id']
MCH_CERT = settings.WECHATPAY_SECRETS['mch_cert']
MCH_KEY = settings.WECHATPAY_SECRETS['mch_key']


QtWeChatPay = partial(WeChatPay, api_key=MCH_API_KEY, mch_id=MCH_ID, mch_cert=MCH_CERT, mch_key=MCH_KEY)


# ----- 生成订单 -----

def create_wechatpay_order(client_label, trade_type, body, price, qt_order_id, qt_product_id, client_ip, openid):
    client = QtWeChatPay(appid=settings.WECHAT_APP_SECRETS[client_label]['appid'])
    wxorder = WeChatOrder(client=client)
    result = wxorder.create(
        trade_type=trade_type,
        body=body,
        total_fee=int(100*float(price)),
        notify_url=WECHAT_NOTIFY_URL,
        out_trade_no=qt_order_id,
        product_id=qt_product_id,
        client_ip=client_ip,
        user_id=openid,
    )
    return result


def parse_wechatpay_unifiedorder_result(result: dict) -> (dict, str):
    """
    解析微信支付请求结果
    :param result: 调用wechatpy.pay.api.WeChatOrder.create方法的请求结果
    :param timestamp: 订单创建的时间戳，JSAPI模式必传；由于微信支付API的返回结果并无时间戳，需要手动传入订单在系统创建的时间，并用此时间戳验证签名
    :return: data: 用以返回的数据
    :return: content_type: Native模式返回HTML，其他模式返回JSON
    """
    trade_type = result['trade_type']

    # Native支付：返回二维码链接code_url
    # References:
    #   - https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=6_5
    if trade_type == 'NATIVE':
        data = {
            'code_url': result['code_url']
        }
        content_type = 'text/html'
        return data, content_type

    # JSAPI支付：返回支付参数和签名，需要携带时间戳
    # 手动计算paySign（WeChatOrder.get_appapi_params 传入的参数有误，不可用）
    # References:
    #  - https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=7_4
    #  - https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=7_4&index=3
    elif trade_type == 'JSAPI':
        pay_sign_data = {
            "appId": result['appid'],
            "timeStamp": str(int(time.time())),
            "nonceStr": result["nonce_str"],
            "package": 'prepay_id={prepay_id}'.format(prepay_id=result["prepay_id"]),
            "signType": 'MD5',
        }
        pay_sign = calculate_signature(pay_sign_data, settings.WECHAT_MCH_API_KEY)
        pay_sign_data["paySign"] = pay_sign
        content_type = 'application/json'
        return pay_sign_data, content_type

    # H5支付：调用微信APP
    # References:
    #   - https://pay.weixin.qq.com/wiki/doc/api/H5.php?chapter=15_4
    elif trade_type == 'MWEB':
        data = {}
        content_type = 'application/json'
        return data, content_type

    # APP支付：调用微信APP
    # References:
    #   - https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=8_1
    elif trade_type == 'APP':
        data = {}
        content_type = 'application/json'
        return data, content_type

    else:
        raise


# ----- 查询订单 -----

def query_wechatpay_order(client_label, transaction_id=None, out_trade_no=None):
    assert transaction_id or out_trade_no, '微信订单ID和用户订单ID不可以同时为空'
    client = QtWeChatPay(appid=settings.WECHAT_APP_SECRETS[client_label]['appid'])
    wxorder = WeChatOrder(client=client)
    result = wxorder.query(transaction_id, out_trade_no)
    return result


# ----- 回调通知 -----

def parse_wechatpay_notify_data(xml):
    data = WeChatPay.get_payment_data(xml)
    appid = data['appid']
    client = WeChatPay(appid=appid, api_key=MCH_API_KEY, mch_id=MCH_ID)
    return client.parse_payment_result(xml)

# -*- coding: utf-8 -*-
"""
企业微信自定义SDK，封装企业微信服务端API制作
"""

import re
import json
import time
import hashlib
import base64
import socket
import struct
from typing import List

import requests
import xmltodict

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from django.core.cache import cache
from django.conf import settings

from qtutils.random import gen_random_str

# 企业微信API根URL
WECHATWORK_API_ROOT_URL = 'https://qyapi.weixin.qq.com/cgi-bin/'

# 企业微信应用密钥
WECHATWORK_SECRETS = settings.WECHATWORK_SECRETS
# 企业ID
CORPID = WECHATWORK_SECRETS['corpid']
# 企业通讯录Secret
CONTACT_SECRET = WECHATWORK_SECRETS['contact']['secret']
CONTACT_TOKEN = WECHATWORK_SECRETS['contact']['token']
CONTACT_ENCODING_AES_KEY = WECHATWORK_SECRETS['contact']['encoding_aes_key']


# ----- Exception -----

class WeChatWorkSdkException(Exception):
    pass


# ----- Access Token -----

def get_access_token(corpid, secret) -> (str, int):
    """
    获取Access Token
    :param corpid: 企业ID
    :param secret: 应用密钥
    :return:
    """
    url = WECHATWORK_API_ROOT_URL + 'gettoken?corpid={corpid}&corpsecret={secret}'\
        .format(corpid=corpid, secret=secret)
    data = json.loads(requests.get(url).content)
    if int(data['errcode']) == 0:
        return data['access_token'], int(data['expires_in'])
    else:
        raise WeChatWorkSdkException(data['errmsg'])


# ----- 客户端数据解密算法 -----

def extract_encrypt(xml_text: str) -> str:
    """
    解析XML中的Encrypt
    :param xml_text:
    :return:
    """
    data = xmltodict.parse(xml_text)['xml']
    return data["Encrypt"]


def cal_encrypt_sign(token: str, timestamp: str, nonce: str, encrypt: str):
    """
    计算签名
    :return:
    """
    # token、timestamp、nonce、msg_encrypt 这四个参数按照字典序排序，拼接为一个字符串
    # hashlib要求b''，必须要encode
    sort_str = "".join(sorted([token, timestamp, nonce, encrypt])).encode()
    # 用sha1算法计算签名
    sha1 = hashlib.sha1()
    sha1.update(sort_str)
    return sha1.hexdigest()


def aes_decrypt(msg_encrypt: str, encoding_aes_key: str) -> str:
    """
    AES算法解密信息
    """
    aes_msg = base64.b64decode(msg_encrypt)  # 对密文base64解码
    aes_key = base64.b64decode(encoding_aes_key + "=")  # EncodingAESKey转AESKey
    random_msg = AES.new(aes_key, AES.MODE_CBC, iv=aes_key[0:16]).decrypt(aes_msg)  # 使用AESKey做AES解密
    pad_num: int = random_msg[-1]  # 去掉补位字符串
    return random_msg[:-pad_num].decode()


def parse_random_msg(random_msg: str) -> dict:
    """
    解析字符串
    """
    # 规则：and_msg = random(16B) + msg_len(4B) + msg + receive_id
    content = random_msg[16:]  # 去掉前16随机字节
    xml_len: int = socket.ntohl(struct.unpack("I", content[: 4].encode())[0])
    msg = content[4: xml_len + 4]  # 截取msg_len 长度的msg
    receive_id = content[xml_len + 4:]  # 剩余字节为receive_id

    # 解析XML明文信息
    data = xmltodict.parse(msg)['xml']
    if data['ToUserName'] != receive_id:
        raise WeChatWorkSdkException("XML数据解密或明文解析错误")
    return dict(data)


def decrypt_msg(xml_text: str, encrypt_sign: str, timestamp: str, nonce: str, token: str, encoding_aes_key: str) -> dict:
    """
    解密客户端消息
    :return:
    """
    # 读取加密信息
    msg_encrypt = extract_encrypt(xml_text=xml_text)
    # 效验签名
    dev_encrypt_sign = cal_encrypt_sign(token, timestamp, nonce, msg_encrypt)
    if dev_encrypt_sign != encrypt_sign:
        raise WeChatWorkSdkException("签名效验不通过")
    # AES算法解密
    random_msg = aes_decrypt(msg_encrypt, encoding_aes_key)
    # 解析随机字符串并把XML数据转成字典
    data = parse_random_msg(random_msg)
    return data


# ----- 服务端数据加密算法 ------

def dict_to_xml(data: dict) -> str:
    xml_str = "<xml>"
    for key, value in data.items():
        pattern = re.compile(r'\d+')
        if not pattern.match(value):
            value = "<![CDATA[{value}]]>".format(value=value)
        xml_item = "<{key}>{value}</{key}>\n".format(key=key, value=value)
        xml_str += xml_item
    xml_str += "</xml>"
    return xml_str


def gen_random_msg(data: dict, random_str_16=None) -> str:
    """
    生成随机字符串
    :param data:
    :param random_str_16: 16位占位符，默认自动生成
    :return: b''
    """
    if random_str_16 is None:
        random_str_16 = gen_random_str(16)
    msg: str = dict_to_xml(data)
    random_msg = random_str_16 + struct.pack("I", socket.htonl(len(msg))).decode() + msg + data['ToUserName']
    return random_msg


def aes_encrypt(random_str: str, encoding_aes_key: str) -> str:
    aes_key = base64.b64decode(encoding_aes_key + "=")  # EncodingAESKey转AESKey
    msg_encrypt = AES.new(aes_key, AES.MODE_CBC, iv=aes_key[0:16]).encrypt(pad(random_str.encode(), 32))  # AES算法加密
    return base64.b64encode(msg_encrypt).decode()


def gen_xml_text(msg_encrypt: str, signature: str, timestamp: str, nonce: str) -> str:
    """
    生成用于发送消息的XML
    :param msg_encrypt:
    :param signature:
    :param timestamp:
    :param nonce:
    :return:
    """
    xml_text = """<xml>
    <Encrypt><![CDATA[{msg_encrypt}]]></Encrypt>
    <MsgSignature><![CDATA[{msg_signature}]]></MsgSignature>
    <TimeStamp>{timestamp}</TimeStamp>
    <Nonce><![CDATA[{nonce}]]></Nonce>
    </xml>""".format(msg_encrypt=msg_encrypt, msg_signature=signature,
                     timestamp=timestamp, nonce=nonce).replace('\n', '').replace('\r', '').replace(' ','')
    return xml_text


def encrypt_msg(data: dict, token: str, encoding_aes_key: str, timestamp=None, nonce=None, random_str_16=None) -> str:
    """
    加密需要发给客户端的消息
    :return:
    """
    if timestamp is None:
        timestamp = str(int(time.time()))
    if nonce is None:
        nonce = gen_random_str(10)  # 不确定随机字符串的要求，按照文档的位数给了10位

    # 加密数据
    random_msg: str = gen_random_msg(data, random_str_16=random_str_16)
    msg_encrypt = aes_encrypt(random_msg, encoding_aes_key)

    # 计算签名
    msg_sign = cal_encrypt_sign(token, timestamp, nonce, msg_encrypt)

    # 生成最终加密XML数据
    return gen_xml_text(msg_encrypt, msg_sign, timestamp, nonce)


# ----- 通用SDK类 -----

class WeChatWorkSDK(object):
    """
    企业微信SDK基本类
    """
    def __init__(self, corpid=None, secret=None, name=None):
        """
        :param corpid:
        :param secret:
        :param name: 自定义的名称
        """
        self.name = name
        if self.name is not None:
            self._access_token_key = 'wechatwork_access_token_' + self.name
        else:
            self._access_token_key = 'wechatwork_access_token'
        if corpid is None:
            # 默认为Django settings传入的corpid
            corpid = CORPID
        self.corpid = corpid
        if secret is None:
            raise WeChatWorkSdkException("secret不可以为空")
        self.secret = secret
        self._api_root_url = WECHATWORK_API_ROOT_URL

    @property
    def access_token(self):
        """
        获取access_token
        详细说明：https://work.weixin.qq.com/api/doc/90000/90135/91039

        首先从缓存中获取；若缓存不存在或者过期，则通过调用接口从企业微信服务器获取并缓存
        property装饰器只是把方法变成属性，每次被调用时依然会调用方法并且返回属性，不会出现缓存过期依然被使用的情况
        :return access_token: str
        """
        try:
            access_token = cache.get(self._access_token_key)
        except KeyError:
            access_token = None

        # access_token缓存为空或者不存在此缓存数据时，都处理为None并且重新请求
        if access_token is None:
            access_token, expires_in = get_access_token(corpid=self.corpid, secret=self.secret)
            cache.set(self._access_token_key, access_token, timeout=int(expires_in))

        return access_token

    def request_api(self, method, api, query_params=None, data=None):
        url = self._api_root_url + api

        # 默认必须传入access_token
        if query_params is None:
            query_params = dict()
        query_params['access_token'] = self.access_token

        # API接口要求必须以JSON格式传入数据
        response = requests.request(method, url, params=query_params, json=data)
        return_data = json.loads(response.content)

        # 抛出异常
        if return_data['errcode'] != 0:
            raise WeChatWorkSdkException(return_data)

        # 返回时删除errcode和errmsg
        return_data.pop('errcode')
        return_data.pop('errmsg')
        return return_data

    def get_api(self, api, query_params=None):
        return self.request_api('GET', api, query_params)

    def post_api(self, api, query_params=None, data=None):
        return self.request_api('POST', api, query_params, data)


class WeChatWorkCallbackSDK(object):
    """
    企业微信回调SDK基本类，用于实现内部系统和企业微信客户端的双向通信
    详细说明：https://work.weixin.qq.com/api/doc/90000/90135/90930
    """
    def __init__(self, token, encoding_aes_key):
        self.token = token
        self.encoding_aes_key = encoding_aes_key

    def encrypt(self, data: dict) -> str:
        """
        服务端加密数据
        :param data:
        :param timestamp:
        :param nonce:
        :return:
        """
        return encrypt_msg(data, token=self.token, encoding_aes_key=self.encoding_aes_key)

    def decrypt(self, xml, sign, timestamp, nonce) -> dict:
        """
        验证并解密来自客户端的数据
        :return:
        """
        return decrypt_msg(xml_text=xml, encrypt_sign=sign, timestamp=timestamp, nonce=nonce,
                           token=self.token, encoding_aes_key=self.encoding_aes_key)


# ------ 企业微信通讯录SDK ------

class ContactSDK(WeChatWorkSDK):
    def __init__(self):
        super().__init__(CORPID, CONTACT_SECRET, 'contact')


class UserSDK(ContactSDK):
    def __init__(self):
        super().__init__()
        # 把默认（父类）API根目录修改成SDK类专用API根目录
        # 先后顺序很重要
        self._api_root_url = self._api_root_url + 'user/'

    def create(self, data: dict):
        """
        :param data:
        必须传入的数据：
        - userid: 企业微信用户的UserID
        - name: 姓名
        - department: 部门，非空列表
        - mobile/email: 手机/邮箱，至少有一个
        :return:
        """
        return self.post_api(api='create', data=data)

    def get(self, userid):
        return self.get_api(api='get', query_params={'userid': userid})

    def update(self, data):
        return self.post_api(api='update', data=data)

    def delete(self, userid):
        return self.get_api(api='delete', query_params={'userid': userid})

    def list(self, department_id=1, fetch_child=True, detail=True) -> List[dict]:
        """
        获取部门成员（详情）
        :param department_id: 获取的部门id，默认根部门
        :param fetch_child: 是否递归获取子部门下面的成员，默认是
        :param detail: 是否获取详情数据，默认是
        :return: 成员列表，每个成员的数据用字典存储
        """
        if detail:
            api = 'list'
        else:
            api = 'simplelist'
        query_params = {'department_id': department_id, 'fetch_child': int(fetch_child)}
        return self.get_api(api=api, query_params=query_params)['userlist']

    def get_active_stat(self, date: str) -> int:
        """
        获取查询日期当天的活跃人数
        :param date: 查询日期，比如'2020-07-06'，最多支持查询30天前数据
        :return: 活跃人数
        """
        # TODO:
        #  - 判断date数据类型并自动转换
        #  - 判断date是否在30天以内
        data = self.post_api(api='get_active_stat', data={'date': date})
        active_cnt = int(data['active_cnt'])
        return active_cnt


class DepartmentSDK(ContactSDK):
    def __init__(self):
        super().__init__()
        self._api_root_url = self._api_root_url + 'department/'

    def create(self):
        pass

    def list(self, depid: str = 1):
        """
        获取指定部门及其下的递归子部门数据
        - 部门ID输入值为1（或者为空）时，默认获取根目录下全量数据
        :param depid: 部门ID
        :return:
        """
        query_params = {'id': depid}
        return self.get_api('list', query_params)


class TagSDK(ContactSDK):
    def __init__(self):
        super().__init__()
        self._api_root_url = self._api_root_url + 'tag/'

    def list(self):
        """
        获取标签列表
        :return:
        """
        return self.get_api('list')


class ContactCallbackSDK(ContactSDK):
    def __init__(self):
        super().__init__()


# ----- 企业微信通讯录回调SDK -----

class ContactCallbackSDK(WeChatWorkCallbackSDK):
    def __init__(self, token, encoding_aes_key):
        super().__init__(token, encoding_aes_key)


# ----- 企业微信身份认证 -----

class WeChatWorkUserAuthSDK(WeChatWorkSDK):
    """
    详见：https://work.weixin.qq.com/api/doc/90000/90135/91437
    """
    pass

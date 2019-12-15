# python lib
import requests
import rsa
import base64
from urllib import parse
from typing import Optional
from ruamel.yaml import YAML
import json
import time

# custom lib
import utils
from storage import Storage
from exceptions import LoginException
from printer import cprint
from account import Account

class LoginException(RuntimeError):
    pass

class Login:

    def __init__(self, 
                 account: Account, 
                 output_file: Optional[str] = None, 
                 yaml=None):
        yaml = yaml if yaml is not None else YAML()
        self.yaml = yaml
        self.output_file = output_file
        self.account = account
        if not account.username or not account.password:
            login_info = self.get_login_info()
            account.username = login_info['username']
            account.password = login_info['password']

    def get_login_info(self):
        print(f'用户 [self.account.uid]: ]')
        username = input('输入账号: ')
        password = input('输入密码: ')
        return { 'username': username, 'password': password }

    def login(self):
        response = login(self.account.username, self.account.password)
        response['user'] = {
            'username': self.account.username, 
            'password': self.account.password, 
        }
        if self.output_file:
            data_file = utils.resolve_to_cwd(self.output_file)
            with open(data_file, mode='w', encoding='UTF-8') as iofile:
                self.yaml.dump(response, iofile)



def login(username, password):
    response = login_simple(username, password)

    # raise errors
    if response.status_code != 200:
        raise LoginException(f'LoginError: ' + response.status_code)
    r_json = response.json()
    if r_json['code'] != 0:
        cprint(r_json['message'], color='red')
        cprint('登录失败（返回值非0）', color='red')
        cprint('解决方法：重启程序再试（建议仅重试一次）', color='green')
        raise LoginException(f'LoginError')

    # handle cookies
    cookies = {}
    cookie_source = [cookie for cookie in r_json['data']['cookie_info']['cookies']]
    for cookie in cookie_source:
        cookies[cookie['name']] = cookie['value']

    # handle tokens
    tokens = {}
    token_source = { key:value for key,value in r_json['data']['token_info'].items() } 
    tokens.update(token_source)

    return { 'app': tokens, 'web': cookies, }



def login_simple(username, password):
    # obtain login key and hash
    response = request_login_key()
    response = response.json()

    if response['code'] != 0:
        raise LoginException(f'LoginError: ' + str(response))

    pem = response['data']['hash']
    key = response['data']['key']
    username, password = encrypt_uname_passwd(key, pem, username, password)

    # login portal
    url = 'https://passport.bilibili.com/api/v3/oauth2/login'
    params = {
            'appkey': Storage.bili['appkey'],
            'channel': 'bili',
            'mobi_app': 'android',
            'platform': 'android',
            'username': username,
            'password': password,
            'ts': str(int(time.time())),
    }
    ## print(f'params: {params}')
    headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    param_str = utils.parse_param(params)

    # create signature
    signature = utils.calc_param_sign(param_str)
    param_str += '&' + 'sign' + '=' + signature
    ## print(f'url: {url}\nparam: {param_str}\nheaders: {headers}\n')
    r = requests.post(url, headers=headers, data=param_str)
    return r

def encrypt_uname_passwd(key, pem, username, password):
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(key.encode())
    password = base64.b64encode(rsa.encrypt(
        (pem + password).encode('utf-8'), pubkey))
    password = parse.quote_plus(password)
    username = parse.quote_plus(username)
    return (username, password)

def request_login_key():
    url = 'https://passport.bilibili.com/api/oauth2/getKey'
    params = {
            'appkey': Storage.bili['appkey']
    }
    param_str = utils.parse_param(params)
    signature = utils.calc_param_sign(param_str)
    params.update( {'sign': signature} )
    response = requests.post(url, data=params)
    return response


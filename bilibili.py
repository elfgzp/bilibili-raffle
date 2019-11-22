# python lib
import asyncio
import aiohttp
from typing import Optional

# custom lib
from account import Account
from printer import cprint
from ratelimiter import RateLimiter
from exceptions import HttpError

class Bilibili:

    instance = None
    client: Optional[aiohttp.ClientSession] = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Bilibili, cls).__new__(cls, *args, **kwargs)
            inst = cls.instance

            inst.banned = False
            inst._session = cls.client
            inst._session_l = RateLimiter(cls.client) \
                    if cls.client is not None \
                    else None
            inst.web_headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/77.0.3865.90 Safari/537.36'),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            }
        return cls.instance

    @property
    def session(self):
        return self._session

    @property
    def rl_session(self):
        return self._session_l

    async def get(self, url, params=None, headers=None, cookies=None, rate_limited: bool = True):
        if rate_limited == True:
            session = self.rl_session
        else:
            session = self.session

        for _ in range(3):
            try:
                response = await session.get(
                        url, params=params, 
                        headers=headers, cookies=cookies, ssl=False)

                response.raise_for_status()

                if response.content_type != 'application/json':
                    r_json = await response.json(content_type=None)
                else:
                    r_json = await response.json()

                if 0 == r_json['code']:
                    return r_json
                else:
                    cprint(f'{r_json}', error=True)
                    return None
            except aiohttp.ClientError as exc:
                cprint(f'aiohttp ClientError: {exc}', color='red')

        raise HttpError(f'Request failed: {response.status} @url {url!r}')


    async def post(self, url, params=None, headers=None, cookies=None, data=None, rate_limited: bool = True):
        if rate_limited == True:
            session = self.rl_session
        else:
            session = self.session

        for _ in range(3):
            # fire request
            try:
                response = await session.post(
                        url, params=params, headers=headers,
                        cookies=cookies, data=data, ssl=False)

                response.raise_for_status()

                if response.content_type != 'application/json':
                    r_json = await response.json(content_type=None)
                else:
                    r_json = await response.json()

                if 0 == r_json['code']:
                    return r_json
                else:
                    cprint(f'{r_json}', error=True)
                    return None
            except aiohttp.ClientError as exc:
                cprint(f'aiohttp ClientError: {exc}', color='red')

        raise HttpError(f'Request failed: {response.status} @url {url!r}')


    async def request_area_list(self):
        url = 'https://api.live.bilibili.com/room/v1/Area/getList'
        headers = self.web_headers.copy()
        response = await self.get(url, headers=headers)
        return response

    async def request_gift_config(self):
        url = 'https://api.live.bilibili.com/gift/v4/Live/giftConfig'
        headers = self.web_headers.copy()
        response = await self.get(url, headers=headers)
        return response

    async def request_check_live_status(self, roomid:int):
        response = await self.request_check_live_info(roomid)
        if response is None:
            return
        if response['code'] == 0:
            return response['data']['live_status']

    async def request_check_live_info(self, roomid:int):
        url = 'https://api.live.bilibili.com/room/v1/Room/get_info'
        headers = self.web_headers.copy()
        params = {
            'room_id': roomid,
        }
        response = await self.get(url, headers=headers, params=params)
        return response

    async def request_check_area(self, 
                                 areaid:int, 
                                 page:int = 1, 
                                 page_size:int = 99):
        '''
        Get a list of rooms in area ``areaid``
        '''

        url = 'https://api.live.bilibili.com/room/v3/area/getRoomList'
        params = {
            'parent_area_id': areaid,
            'page': page, 
            'page_size': page_size, 
        }
        headers = self.web_headers.copy()

        response = await self.get(url, headers=headers, params=params)
        return response

    async def request_check_room(self, 
                                 roomid:int, 
                                 rate_limited: bool = False, 
                                 account: Optional[Account] = None):
        '''
        Check for lottery in room ``roomid``
        '''

        url = 'https://api.live.bilibili.com/xlive/lottery-interface/v1/lottery/Check'
        params = { 'roomid': roomid }
        headers = self.web_headers.copy()
        cookies = account.web_cookies.copy() if account is not None else None
        response = await self.get(url, 
                                  headers=headers, 
                                  params=params, 
                                  rate_limited=rate_limited, 
                                  cookies=cookies)
        return response

    async def request_live_count(self):
        url = 'https://api.live.bilibili.com/room/v1/Area/getLiveRoomCountByAreaID'
        params = { 'areaId': 0 }
        headers = self.web_headers.copy()
        response = await self.get(url, params=params, headers=headers)
        return response

    async def request_live_recommendation(self, page:int, page_size:int=30):
        url = 'https://api.live.bilibili.com/room/v1/room/get_user_recommend'
        page_size = 100 if page_size > 100 else page_size
        params = { 'page': page , 'page_size': page_size }
        headers = self.web_headers.copy()
        response = await self.get(url, params=params, headers=headers)
        return response

    async def post_join_raffle(self, 
                               post_data: dict, 
                               account: Optional[Account] = None):
        if account is None or account.banned:
            return

        url = 'https://api.live.bilibili.com/xlive/lottery-interface/v5/smalltv/join'
        headers = self.web_headers.copy()
        cookies = account.web_cookies.copy()
        for _ in range(3):
            response = await self.rl_session.post(
                    url, headers=headers,
                    cookies=cookies, data=post_data)
            try:
                response.raise_for_status()
                js = await response.json()
                
                if 0 == js['code']:
                    return js
                elif '访问被拒绝' == js.get('message'):
                    account.banned = True
                    account.cprint(f'访问被拒绝', color='purple')
                    return None
                else:
                    cprint(f'{js}', color='red')
                    return None
            except (aiohttp.ClientPayloadError, 
                    aiohttp.ClientResponseError) as exc:
                cprint(f'aiohttp ClientError: {exc}', color='red')

    async def post_join_guard(self, 
                              post_data: dict, 
                              account: Optional[Account] = None):
        if account is None or account.banned:
            return

        url = 'https://api.live.bilibili.com/xlive/lottery-interface/v3/guard/join'
        headers = self.web_headers.copy()
        cookies = account.web_cookies.copy()
        for _ in range(3):
            response = await self.rl_session.post(
                    url, headers=headers,
                    cookies=cookies, data=post_data)
            try:
                response.raise_for_status()
                js = await response.json()
                
                if 0 == js['code']:
                    return js
                elif '访问被拒绝' == js.get('message'):
                    account.banned = True
                    account.cprint(f'访问被拒绝', color='purple')
                    return None
                else:
                    return None
            except (aiohttp.ClientPayloadError, 
                    aiohttp.ClientResponseError) as exc:
                cprint(f'aiohttp ClientError: {exc}', color='red')

    # {"code":0,"msg":"ok","message":"ok","data":[]}
    async def post_room_entry(self, 
                              roomid: int, 
                              account: Optional[Account] = None):
        if account is None:
            return

        url = 'https://api.live.bilibili.com/room/v1/Room/room_entry_action'
        headers = self.web_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        cookies = account.web_cookies.copy()
        data = {
            'room_id': roomid,
            'platform': 'pc',
            'csrf_token': cookies['bili_jct'],
            'csrf': cookies['bili_jct'],
            'visit_id': '',
        }
        response = await self.post(
                url, data=data, headers=headers, cookies=cookies)
        return response


    async def post_open_club_award(self, 
                                   item_id: str, 
                                   account: Account):
        if account is None or item_id not in [ str(i) for i in range(1, 1+6) ]:
            return

        url = 'https://api.live.bilibili.com/activity/v1/UnionFans/openPrivilege'
        headers = self.web_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        cookies = account.web_cookies.copy()
        data = {
            'id': item_id, 
            'csrf_token': cookies['bili_jct'], 
            'csrf': cookies['bili_jct'], 
        }
        response = await self.post(
                url, data=data, headers=headers, cookies=cookies)
        return response


    async def request_club_award(self, account: Account):
        '''
        "code": 0, 
        "data": {
            "money_num": "60672765",
            "list": {
                "1": 1, // 1 (未)   2 (已)
                "2": 1,
                "3": 1,
                "4": 1,
                "5": 1,
                "6": 1
            }
        }
        '''
        if account is None:
            return

        url = 'https://api.live.bilibili.com/activity/v1/UnionFans/getPrivilege'
        headers = self.web_headers.copy()
        cookies = account.web_cookies.copy()
        response = await self.get(
                url, headers=headers, cookies=cookies)
        return response


    async def request_task_info(self, account: Account):
        if account is None:
            return

        url = 'https://api.live.bilibili.com/i/api/taskInfo'
        headers = self.web_headers.copy()
        cookies = account.web_cookies.copy()
        response = await self.get(
                url, headers=headers, cookies=cookies)
        return response


    async def post_checkin(self, account: Account):
        if account is None:
            return

        url = 'https://api.live.bilibili.com/sign/doSign'
        headers = self.web_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        cookies = account.web_cookies.copy()
        response = await self.get(
                url, headers=headers, cookies=cookies)
        return response


    async def post_obtain_double_award(self, account: Account):
        if account is None:
            return

        url = 'https://api.live.bilibili.com/activity/v1/task/receive_award'
        headers = self.web_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        cookies = account.web_cookies.copy()
        data = {
            'task_id': 'double_watch_task', 
            'csrf_token': cookies['bili_jct'], 
            'csrf': cookies['bili_jct'], 
        }
        response = await self.post(
                url, data=data, headers=headers, cookies=cookies)
        return response


    async def post_user_online_heart(self, account: Account):
        if account is None:
            return

        url = 'https://api.live.bilibili.com/User/userOnlineHeart'
        headers = self.web_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        cookies = account.web_cookies.copy()
        data = {
            'csrf_token': cookies['bili_jct'], 
            'csrf': cookies['bili_jct'], 
            'visit_id': '', 
        }
        response = await self.post(
                url, data=data, headers=headers, cookies=cookies)
        # {"code":0,"msg":"OK","message":"OK","data":{"giftlist":[]}}
        return response


    async def post_bag_gift(self, account: Account, data: dict):
        if account is None:
            return

        url = 'https://api.live.bilibili.com/gift/v2/live/bag_send'
        headers = self.web_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        cookies = account.web_cookies.copy()
        response = await self.post(
                url, data=data, headers=headers, cookies=cookies)
        return response


# python lib
import json
import random
import asyncio
from typing import Optional

# custom lib
from bilibili import Bilibili
from account import Account
from printer import cprint


async def handle_raffle(gift_data: dict, account: Optional[Account] = None):
    # check that gift was not obtained
    if account is None:
        return

    entry = await Bilibili().post_room_entry(gift_data['roomid'], account)
    # valid = await ensure_unposted(
    #     gift_data['roomid'], 
    #     gift_data.get('id') or gift_data.get('raffleId'), 
    #     account,
    # )
    # if not valid:
    #     return

    await asyncio.sleep(random.randrange(3, 10))

    if gift_data['type'] == 'guard':
        # post guard
        response = await Bilibili().post_join_guard(gift_data, account)
    elif gift_data['type'] == 'pk':
        # post pk
        response = await Bilibili().post_join_pk(gift_data, account)
    else:
        # post gift
        response = await Bilibili().post_join_raffle(gift_data, account)

    gid = gift_data.get('id') or gift_data.get('raffleId')
    roomid = gift_data['roomid']

    if response is not None and response['code'] == 0:
        data = response['data']
        if gift_data['type'] == 'guard':
            award = data.get('award_text', '')
            account.cprint(f'{gid:<13} {award}', color='green')
        elif gift_data['type'] == 'pk':
            award = data.get('award_text', '')
            account.cprint(f'{gid:<13} {award}', color='green')
        else:
            award = data.get('award_name', '')
            award += f'+{data.get("award_num", "")}'
            account.cprint(f'{gid:<13} @{roomid:<11} {award}', color='green')
    else:
        account.cprint(f'{gid:<13} @{roomid:<11} 获取失败', color='red')


async def ensure_unposted(roomid, checkid, account):
    verify = await Bilibili().request_check_room(
        roomid, 
        True, 
        account, 
    )
    unposted = [ i['id'] for i in verify['data']['guard'] ]
    unposted += [ i['raffleId'] for i in verify['data']['gift'] ]
    unposted += [ i['id'] for i in verify['data']['pk'] ]
    return (checkid in unposted)



class Raffle:

    def __init__(self, 
                 emitter,
                 account: Optional[Account] = None, 
                 loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        loop = loop if loop is not None else asyncio.get_event_loop()
        self.loop = loop
        self.emitter = emitter
        self.account = account

        if emitter is not None:
            @emitter.on('gift')
            async def join_gift(gift):
                # roomid, id, type, name
                gift_data = {
                    'type': gift['type'], 
                    'roomid': gift['roomid'], 
                    'id': gift['id'], 
                    'csrf': account.web_cookies['bili_jct'], 
                    'csrf_token': account.web_cookies['bili_jct'],
                    'visit_id': '', 
                }
                await handle_raffle(gift_data, account)

            @emitter.on('guard')
            async def join_guard(guard):
                guard_data = {
                    'type': guard['type'], 
                    'roomid': guard['roomid'], 
                    'id': guard['id'], 
                    'csrf': account.web_cookies['bili_jct'], 
                    'csrf_token': account.web_cookies['bili_jct'], 
                    'visit_id': '', 
                }
                await handle_raffle(guard_data, account)

            @emitter.on('pk')
            async def join_pk(pk):
                pk_data = {
                    'type': pk['type'],
                    'roomid': pk['roomid'],
                    'id': pk['id'],
                    'csrf': account.web_cookies['bili_jct'], 
                    'csrf_token': account.web_cookies['bili_jct'], 
                    'visit_id': '', 
                }
                await handle_raffle(pk_data, account)

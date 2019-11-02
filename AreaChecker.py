# python lib
import asyncio
import requests

# custom lib
from bilibili import Bilibili
from printer import cprint


class AreaList:

    AREAS = None

    @classmethod
    async def arealist(cls):
        if cls.AREAS is None:
            response = await Bilibili().request_area_list()
            arealist = response['data']
            cls.AREAS = {}
            [cls.AREAS.update({ area['id']: area['name'] }) \
                    for area in arealist]
        return cls.AREAS


async def get_all_rooms():
    response = await Bilibili().request_live_count()
    count = response['data']['num']

    page_size = 99
    for page in range(1, count//page_size + 2):
        async for room in get_all_rooms_on_page(page, page_size=page_size):
            yield room

async def get_all_rooms_on_page(page:int, 
                                page_size:int = 99, 
                                popularity_over:int = 50):
    response = await Bilibili().request_check_area(0, page=page, page_size=page_size)
    if response['code'] != 0:
        cprint(f'Status code in get_all_rooms_on_page '
               f'{response["code"]} {response["message"]}', color='red')
        raise RuntimeError('Status code nonzero')
    for room_info in response['data']['list']:
        if room_info['online'] > popularity_over:
            yield room_info['roomid']

async def get_room_from_each_area():
    for areaid in range(1,7):
        # {areaid: roomid}
        area_room_map = await get_room_from_area(areaid)
        if area_room_map is not None:
            yield area_room_map

async def get_room_from_area(areaid: int):
    if areaid not in range(1, 1+7):
        return None

    response = await Bilibili().request_check_area(
            areaid, page=1, page_size=10)

    rooms = response['data']['list']
    if len(rooms) == 0:
        return None
    for room in rooms:
        roomid = room['roomid']
        status = await Bilibili().request_check_live_status(roomid)
        if status == 1:
            return { 'areaid': areaid, 'roomid': roomid }

async def get_area_of_room(roomid: int):
    response = await Bilibili().request_check_live_info(roomid)
    if response is None:
        return
    if response['code'] == 0:
        return response['data']['parent_area_id']
    else:
        cprint(f'Get area of room status code {response["code"]}', 
               color='red')


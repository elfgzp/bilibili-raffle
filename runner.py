# python lib
import asyncio
from pyee import AsyncIOEventEmitter
from ruamel.yaml import YAML
from typing import Optional

# custom lib
import utils
from login import Login
from raffle import Raffle
from printer import cprint
from storage import Storage
from account import Account
from bilibili import Bilibili
from exceptions import LoginException
from AreaChecker import AreaList
from rafflereceiver import RaffleReceiver
from SessionController import new_session


class Runner:

    '''
    This class reads the configuration, sign in (optional) to bilibili, 
    attempts to connect to the server and if successful, listens to the
    push notifications.
    '''

    def __init__(self, 
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        loop = loop if loop is not None else asyncio.get_event_loop()
        self.loop = loop
        self.yaml = None
        self.aiohttp_session = None
        self.aiohttp_session_waiter = None
        self.aiohttp_session_closer = None
        self.raffle_emitter = None

        self.servers = None
        self.account_files = []
        self.accounts = []

        self.yaml = YAML()

        waiter, closer = new_session(loop=self.loop, 
                                     headers={ 'Connection': 'close' }, 
                                     raise_for_status=True)
        self.aiohttp_session_waiter = waiter
        self.aiohttp_session_closer = closer

    def read_config(self):
        data_file = utils.resolve_to_cwd('config.yaml')
        with open(data_file, mode='r', encoding='UTF-8') as iofile:
            settings = self.yaml.load(iofile)
            self.account_files = settings['users']
            self.servers = settings['servers']
            Storage.bili = settings['bilibili']
            Storage.servers = self.servers

    def process_login(self):
        accounts = [ Account(data_file, self.yaml) for data_file in self.account_files ]
        self.accounts = accounts
        for acc in accounts:
            if not acc.usable and acc.username and acc.password:
                l = Login(acc, output_file=acc.input_file, yaml=self.yaml)
                try:
                    cprint(f'{acc.input_file!r}: Logging in...', color='green')
                    l.login()
                    acc.reload()
                except LoginException as exc:
                    acc.cprint(f'登录失败 - {exc}', error=True)
            elif acc.usable:
                msg = (f'{acc.input_file!r}: cookies读取成功')
                acc.cprint(f'{msg}', color='green')
            else:
                msg = (f'登录信息不完整 && cookies未提供. - '
                       f' {acc.input_file!r} Skipped.')
                cprint(f'{msg}', color='yellow')


    async def run(self):
        self.read_config()
        self.process_login()

        self.aiohttp_session = await self.aiohttp_session_waiter

        Bilibili.client = self.aiohttp_session

        await AreaList.arealist()

        self.raffle_emitter = AsyncIOEventEmitter(loop=self.loop)

        # 监听抽奖event 执行抽奖
        raffles = [ Raffle(self.raffle_emitter, loop=self.loop, account=a) 
                           for a in self.accounts
                           if a.usable ]

        servers = self.servers

        receiver = RaffleReceiver(servers, 
                                  emitter=self.raffle_emitter, 
                                  loop=self.loop).run()

        done, pending = await asyncio.wait(
            [
                receiver, 
            ], 
            loop=self.loop, 
            return_when=asyncio.FIRST_EXCEPTION, 
        )

        await self.aiohttp_session_closer.close_session()

        for task in done:
            if task.exception():
                raise task.exception()


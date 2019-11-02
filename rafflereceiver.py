# python lib
import sys
import asyncio
import struct
import json
import pyee
import websockets

# custom lib
from printer import cprint


class RaffleReceiver:

    ACCEPTED = 8
    RAFFLE_MSG = 5

    def __init__(self, url, emitter=None, loop=None, password=None):
        self.url = url
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.emitter = emitter
        self.password = password or ''
        self.ws = None
        self.again = True
        self.accepted = False

    async def run(self):
        while self.again:
            try:
                await self.connect()
                msg = (f'ConnectionRefused: Password mismatch')
                if not self.accepted:
                    cprint(f'{msg}', error=True)
                    sys.exit(1)
            except ConnectionRefusedError:
                msg = (f'ConnectionRefused: Server may be down (Retrying in 120s)')
                cprint(f'{msg}', color='yellow')
                await asyncio.sleep(120)

    async def connect(self):
        cls = self.__class__
        async with websockets.connect(self.url) as ws:
            self.ws = ws
            accepted = False
            try:
                await ws.send(self.handshake)

                response = await ws.recv()
                msgs = self.decode_msg(response)
                handshake_resp = msgs[0]
                if handshake_resp['cmd'] == cls.ACCEPTED:
                    self.accepted = accepted = True
                    cprint(f'Established connection with [ {ws.remote_address} ]', color='green')

                while accepted and ws.open:
                    data = await ws.recv()
                    msgs = self.decode_msg(data)
                    for msg in msgs:
                        if msg['cmd'] == cls.RAFFLE_MSG:
                            body = self.deserialize(msg['body'])
                            self.on_raffle(body)

                await self.close()
                await self.wait_closed()
                self.accepted = False
            except websockets.ConnectionClosed:
                if accepted:
                    cprint(f'Lost connection: [ {ws.remote_address} ]', color='red')
                self.again = True
            except IndexError:
                pass
            except Exception as exc:
                cprint(f'{type(exc)}: {exc}', error=True)


    def on_raffle(self, data):
        t = 'gift' if data['type'] != 'guard' else 'guard'
        self.emitter and self.emitter.emit(t, data)
        cprint(f'{data["id"]:<13} @{data["roomid"]:<12} {data["name"]}', 
            color='cyan')

    def deserialize(self, json_str):
        try:
            json_str = json_str.decode('utf-8')
        except AttributeError:
            pass
        return json.loads(json_str)

    @property
    def handshake(self):
        contract = {
            'password': self.password, 
        }
        payload = json.dumps(contract)
        return self.prepare_msg(7, payload)

    def decode_msg(self, msg):
        messages = []
        body = ''
        while len(msg) > 0:
            total_len, header_len, _, cmd, _ = struct.unpack('!IHHII', msg[:16])
            body = msg[header_len:total_len]
            msg = msg[total_len:]
            messages.append( { 'cmd': cmd, 'body': body } )
        return messages


    def prepare_msg(self, cmd, msg=''):
        body = b''
        try:
            msg = msg.encode('utf-8')
            body += msg
        except AttributeError:
            pass

        header = struct.pack('!IHHII', len(body) + 16, 16, 1, cmd, 1)

        payload = b''
        payload += header
        payload += body

        return payload

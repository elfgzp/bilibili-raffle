# python lib
import sys
import asyncio
import struct
import json
import pyee
import websockets

# custom lib
from printer import cprint


class NoAvailableServer(RuntimeError):
    pass

class RaffleReceiver:

    ACCEPTED = 8
    RAFFLE_MSG = 5

    def __init__(self, servers, emitter=None, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.emitter = emitter
        self.ws = None
        self.again = True
        self.accepted = False
        self.connected = False

        self.timeout_detector = None

        self.index = 0
        self.servers = servers
        self.server = None
        if self.servers is not None:
            self.server = self.next_server()


    async def run(self):
        while self.again and self.server != None:
            try:
                done, pending = await asyncio.wait(
                    [
                        self.timeout(), 
                        self.connect(), 
                    ], 
                    loop=self.loop, 
                    return_when=asyncio.FIRST_EXCEPTION, 
                )

                try:
                    for task in done:
                        if task.exception():
                            raise task.exception()

                    if not self.accepted:
                        msg = (f'ConnectionRefused: Password mismatch')
                        cprint(f'{msg}', error=True)
                        sys.exit(1)
                except (ConnectionRefusedError, TimeoutError, OSError):
                    await self.on_refused()
                except websockets.InvalidMessage:
                    pass
            except NoAvailableServer:
                cprint(f'NoAvailableServer: Stop connecting.', error=True)
                self.again = False
                self.server = None
            finally:
                for task in pending:
                    try:
                        task.cancel()
                        await task
                    except Exception:
                        pass

    
    async def timeout(self):
        await asyncio.sleep(10)
        if False == self.connected:
            raise TimeoutError()
        
    async def on_refused(self):
        msg = (f'ConnectionRefused: Server may be down. ')
        self.server = self.next_server()
        msg += f'(Switching to {self.server["address"]})'
        cprint(f'{msg}', color='yellow')

    async def connect(self):
        cls = self.__class__
        url = f'ws://{self.server["address"]}:{self.server["port"]}'
        async with websockets.connect(url) as ws:
            self.connected = True
            self.ws = ws
            accepted = False
            try:
                await ws.send(self.handshake)

                size = 0
                response = b''
                while (size < 16):
                    response += await ws.recv()
                    size += len(response)
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

                await ws.close()
                await ws.wait_closed()
                self.accepted = False
            except websockets.ConnectionClosed:
                if accepted:
                    cprint(f'Lost connection: [ {ws.remote_address} ]', color='red')
                self.again = True
            except IndexError:
                pass
            except Exception as exc:
                cprint(f'{type(exc)}: {exc}', error=True)
                self.again = False
            finally:
                self.connected = False


    def on_raffle(self, data):
        t = ''
        if data['type'] == 'guard':
            t = 'guard'
        elif data['type'] == 'pk':
            t = 'pk'
        else:
            t = 'gift'
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
            'password': self.server['password'], 
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

    def next_server(self):
        server = None

        try:
            if self.servers is not None and len(self.servers) != 0:
                self.index %= len(self.servers)
                server = self.servers[self.index]
                self.index += 1
            else:
                self.again = False
                raise NoAvailableServer('No available server')
        except IndexError:
            raise NoAvailableServer('No available server')

        return server

import telnetlib3
import asyncio
from threading import Thread, Event
from queue import Queue
import time


class LogHandler:
    def __init__(self, host, port=23):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.stop_event = Event()
        self.log_queue = Queue()
        self.connected = False
        self.read_thread = None
        self.loop = None
        self._running = False

    async def async_connect(self):
        try:
            print(f"Attempting to connect to {self.host}:{self.port}")
            self.reader, self.writer = await telnetlib3.open_connection(
                self.host,
                self.port,
                connect_minwait=0.1,
                connect_maxwait=1.0
            )
            print("Connection established")
            self.connected = True

            # Send the tail command after a short delay
            await asyncio.sleep(1)
            self.writer.write('tail -f /var/log/messages\r\n')
            await self.writer.drain()

            return True
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            self.connected = False
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
            return False


    async def read_loop(self):
        try:
            while self._running and not self.stop_event.is_set():
                try:
                    data = await self.reader.read(1024)
                    if not data:
                        break
                    decoded_data = data
                    #print(f"Received data: {decoded_data}")
                    self.log_queue.put(decoded_data)
                except Exception as e:
                    print(f"Error reading data: {e}")
                    break
        except Exception as e:
            print(f"Error in read loop: {e}")
        finally:
            self._running = False
            self.connected = False

    def run_async_loop(self):

        async def main():
            try:
                if await self.async_connect():
                    self._running = True
                    await self.read_loop()
            finally:
                self._running = False
                if self.writer:
                    self.writer.close()
                    await self.writer.wait_closed()

        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(main())
        except Exception as e:
            print(f"Error in async loop: {e}")
        finally:
            try:
                self.loop.close()
            except:
                pass

    def connect(self):
        try:
            self.read_thread = Thread(target=self.run_async_loop, daemon=True)
            self.read_thread.start()

            # Wait for connection to be established
            timeout = 5
            while timeout > 0 and not self.connected:
                time.sleep(0.1)
                timeout -= 0.1

            return self.connected
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        self._running = False
        self.stop_event.set()

        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)

        self.connected = False
        self.reader = None
        self.writer = None

    def send_command(self, command):
        if not self.connected or not self.writer:
            return False

        async def _send():
            try:
                self.writer.write(command + '\r\n')
                await self.writer.drain()
                return True
            except Exception as e:
                print(f"Error sending command: {e}")
                return False

        if self.loop and not self.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(_send(), self.loop)
            try:
                return future.result(timeout=5)
            except Exception as e:
                print(f"Error sending command: {e}")
                return False
        return False
        

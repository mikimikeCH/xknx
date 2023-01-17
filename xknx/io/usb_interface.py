import logging

from xknx.io.connection import ConnectionConfigUSB
from xknx.io.usb_client import USBClient
from xknx.telegram import Telegram

from .interface import Interface

logger = logging.getLogger("xknx.log")


class USBInterface(Interface):
    """USB implementation of the abstract `Interface` class"""

    def __init__(self, xknx, connection_config: ConnectionConfigUSB) -> None:
        self.xknx = xknx
        self.connection_config = connection_config
        self.usb_client: USBClient = USBClient(xknx, connection_config)

    async def start(self) -> None:
        """Start the USB interface
        Tries to find the specified USB device or if not provided,
        searches for known devices.

        Once a device is found, the send and receive threads are started.

        Raises
        ------
        USBDeviceNotFoundError
            if no USB device with idVendor and idProduct can be found
        """
        self.usb_client.start()

    async def stop(self) -> None:
        """Stops the USB interface by stopping the USB send and receive threads"""
        self.usb_client.stop()

    async def connect(self) -> bool:
        """Connect to KNX bus. Returns True on success."""
        return self.usb_client.connect()

    async def disconnect(self) -> None:
        """Disconnect from KNX bus."""
        self.usb_client.disconnect()

    async def send_telegram(self, telegram: Telegram) -> None:
        """Send Telegram to KNX bus."""
        self.usb_client.send_telegram(telegram=telegram)
import threading
import gatt
import gi.repository.GLib as glib
from bluetooth import (
    InfiniTimeDevice,
    InfiniTimeManager,
    BluetoothDisabled,
    NoAdapterFound,
)
from config import config


class Worker:
    def __init__(self):
        self.conf = config()
        self.manager = InfiniTimeManager()
        self.mac_address = None
        self.device = None
        self.mac_address = "d7:dc:1c:87:57:1f"
        self.mainloop = glib.MainLoop()

    def disconnect_paired_device(self):
        try:
            devices = self.manager.devices()
            for d in devices:
                if d.mac_address == self.manager.get_mac_address() and d.is_connected():
                    d.disconnect()
        finally:
            self.conf.set_property("paired", "False")

    def do_scanning(self):
        print("Start scanning")
        if not self.manager:
            # create manager if not present yet
            try:
                self.manager = InfiniTimeManager()
            except (gatt.errors.NotReady, BluetoothDisabled):
                print("Bluetooth is disabled")
            except NoAdapterFound:
                print("No bluetooth adapter found")
        if not self.manager:
            return

        if self.conf.get_property("paired"):
            print("Paired device found")
            self.disconnect_paired_device()
            print("Paired device disconnected")

        self.manager.scan_result = False
        try:
            self.manager.scan_for_infinitime()
        except (gatt.errors.NotReady, gatt.errors.Failed) as e:
            print(e)
            self.destroy_manager()
        try:
            for mac in self.manager.get_device_set():
                print("Found {}".format(mac))
                self.mac_address = mac
        except AttributeError as e:
            print(e)
            self.destroy_manager()
        print("Scanning finished")
        self.manager.set_mac_address(self.mac_address)
        mainloop = glib.MainLoop()

    def start(self):
        self.device = InfiniTimeDevice(manager=self.manager, mac_address=worker.mac_address, thread=False)
        self.device.connect()

    def run_loop(self):
        self.mainloop.run()

    def stop(self):
        self.mainloop.quit()
        self.device.disconnect()


if __name__ == "__main__":
    worker = Worker()
    worker.conf.set_property("paired", "False")

    if worker.conf.get_property("paired"):
        print("Paired device found")
    else:
        worker.do_scanning()
        worker.conf.set_property("paired", "True")
    worker.start()
    thread = threading.Thread(target=worker.run_loop, daemon=False)
    thread.start()
    print("MAC:", worker.mac_address)
    noti = {"category": "SMS", "sender": "Durva Trivedi", "message": "Hello!! :D"}
    input("Press Enter to send notification")
    worker.device.send_notification(noti)
    input("Press Enter to exit")
    worker.stop()
    worker.device.disconnect()

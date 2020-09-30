from .utils import Table
import struct


class ControlValueTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        n = len(self.data.read())
        self.data.seek(0)
        self.control_values = struct.unpack(f"{n // 2}H", self.data.read())
        del self.data

    def pack(self):
        return struct.pack(f"{len(self.control_values)}H" * self.control_values)

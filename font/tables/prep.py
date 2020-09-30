from .utils import Table
import struct


class ControlValueProgramTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        n = len(self.data.read())
        self.data.seek(0)
        self.control_value_program = struct.unpack(f"{n}B", self.data.read())
        del self.data

    def pack(self):
        return struct.pack(
            f"{len(self.control_value_program)}B", *self.control_value_program
        )

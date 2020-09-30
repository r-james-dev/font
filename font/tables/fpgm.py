from .utils import Table
import struct


class FontProgramTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        n = len(self.data.read())
        self.data.seek(0)
        self.instructions = struct.unpack(f"{n}B", self.data.read())
        del self.data

    def pack(self):
        return struct.pack(f"{len(self.instructions)}B", *self.instructions)

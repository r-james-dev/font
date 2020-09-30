from .utils import Table
import struct

ltsh_s = struct.Struct(">2H")


class LinearThresholdTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        _, num_glyphs = ltsh_s.unpack(self.data.read(4))
        self.y_pels = struct.unpack(f"{num_glyphs}B", self.data.read(num_glyphs))
        del self.data

    def pack(self):
        return ltsh_s.pack(0, len(self.y_pels)) + struct.pack(
            f"{len(self.y_pels)}B", *self.y_pels
        )

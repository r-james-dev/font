from .utils import Table, SBitLineMetrics
import struct

ebsc_h_s = struct.Struct(">2HI")
ebsc_bitmap_scale_s = struct.Struct("4B")


class BitmapScaleTable(object):
    def __init__(self, data):
        self.hori = SBitLineMetrics(data)
        self.vert = SBitLineMetrics(data)
        (
            self.ppem_x,
            self.ppem_y,
            self.substitute_ppem_x,
            self.substitute_ppem_y,
        ) = ebsc_bitmap_scale_s.unpack(data.read(4))

    def pack(self):
        return (
            self.hori.pack()
            + self.vert.pack()
            + ebsc_bitmap_scale_s.pack(
                self.ppem_x, self.ppem_y, self.substitute_ppem_x, self.substitute_ppem_y
            )
        )


class EmbeddedBitmapScalingTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        _, _, num_sizes = ebsc_h_s.unpack(self.data.read(8))
        self.bitmap_scale_tables = [
            BitmapScaleTable(self.data) for _ in range(num_sizes)
        ]
        del self.data

    def pack(self):
        return ebsc_h_s.pack(2, 0, len(self.bitmap_scale_tables)) + b"".join(
            table.pack for table in self.bitmap_scale_tables
        )

from .utils import Table
import struct

gcid_s = struct.Struct(">2HIH64sH64s2H")


class GlyphToCIDMappingTable(Table):
    def __init__(self, *args):
        super().__init__(self, *args)
        (
            _,
            _,
            _,
            self.registry,
            registry_name,
            self.order,
            order_name,
            self.supplement_version,
            count,
        ) = gcid_s.unpack(self.data.read(124))
        self.registry_name = registry_name.rstrip("\0")
        self.order_name = order_name.rstrip("\0")
        self.cids = struct.unpack(f">{count}H", self.data.read(2 * count))
        del self.data

    def pack(self, *args):
        return gcid_s.pack(
            0,
            0,
            124 + 2 * len(self.cids),
            self.registry,
            self.registry_name[:64].ljust(64, "\0"),
            self.order,
            self.order_name[:64].ljust(64, "\0"),
            self.supplement_version,
            len(self.cids),
        ) + struct.pack(f">{len(self.cids)}H", *self.cids)

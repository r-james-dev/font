from .utils import Table
import struct

gasp_s = struct.Struct(">2H")


class GaspRangeRecord(object):
    def __init__(self, data):
        (self.range_max_ppem, self.range_gasp_behavior) = gasp_s.unpack(data.read(4))

    def pack(self):
        return gasp_s.pack(self.range_max_ppem, self.range_gasp_behavior)


class GridFittingAndScanConversionProcedureTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        _, num_ranges = gasp_s.unpack(self.data.read(4))
        self.records = sorted(
            [GaspRangeRecord(self.data) for _ in range(num_ranges)],
            key=lambda x: x.range_max_ppem,
        )
        del self.data

    def pack(self, *args):
        self.records = sorted(self.records, key=lambda x: x.range_max_ppem)
        return gasp_s.pack(1, len(self.records)) + b"".join(
            record.pack() for record in self.records
        )

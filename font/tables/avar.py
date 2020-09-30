from .utils import Table
import struct

avar_h_s = struct.Struct(">4H")
avar_segment_maps_s = struct.Struct(">H")
avar_axis_value_map_s = struct.Struct(">2H")


class AxisValueMapRecord(object):
    def __init__(self, data):
        (self.from_coordinate, self.to_coordinate) = avar_axis_value_map_s.unpack(
            data.read(4)
        )
        self.from_coordinate /= 2 ** 14
        self.to_coordinate /= 2 ** 14

    def pack(self):
        return avar_axis_value_map_s.pack(
            int(self.from_coordinate * 2 ** 14), int(self.to_coordinate * 2 ** 14)
        )


class SegmentMapRecord(object):
    def __init__(self, data):
        position_map_count = avar_segment_maps_s.unpack(data.read(2))
        self.axis_value_maps = [
            AxisValueMapRecord(data) for _ in range(position_map_count)
        ]

    def pack(self):
        return avar_segment_maps_s.pack(len(self.axis_value_maps)) + b"".join(
            table.pack() for table in self.axis_value_maps
        )


class AxisVariationsTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        (_, _, _, axis_count) = avar_h_s.unpack(self.data.read(8))
        self.axis_segment_maps = [
            SegmentMapRecord(self.data) for _ in range(axis_count)
        ]
        del self.data

    def pack(self):
        return avar_h_s.pack(1, 0, 0, len(self.axis_segment_maps)) + b"".join(
            table.pack() for table in self.axis_segment_maps
        )

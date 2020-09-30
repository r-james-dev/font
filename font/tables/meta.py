from ..utils import str2tag, tag2str
from .utils import Table
import struct

meta_h_s = struct.Struct(">4I")
meta_data_map_s = struct.Struct(">3I")


class DataMapRecord(object):
    def __init__(self, data):
        (tag, data_offset, data_length) = meta_data_map_s.unpack(data.read(12))
        self.tag = tag2str(tag)
        start = data.tell()
        data.seek(data_offset)
        self.data = data.read(data_length)
        data.seek(start)

        if self.tag in ["dlng", "slng"]:
            self.data = self.data.decode("utf-8")

    def pack(self, offset):
        data = self.data
        if self.tag in ["dlng", "slng"]:
            data = self.data.encode("utf-8")

        return meta_data_map_s.pack(str2tag(self.tag), offset, len(data)), data


class MetadataTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        (_, _, _, data_maps_count) = meta_h_s.unpack(self.data.read(16))
        self.data_maps = [DataMapRecord(self.data) for _ in range(data_maps_count)]
        del self.data

    def pack(self):
        header = meta_h_s.pack(1, 0, 0, len(self.data_maps))
        datablock = b""
        offset = 16 + 12 * len(self.data_maps)
        for map in self.data_maps:
            data = map.pack(offset)
            header += data[0]
            datablock += data[1]
            offset += len(data[1])

        return header + datablock

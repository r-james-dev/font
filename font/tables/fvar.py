from ..utils import str2tag, tag2str
from .utils import Table
import struct

fvar_h_s = struct.Struct(">8H")
fvar_variation_axis_record_s = struct.Struct(">4I2H")
fvar_instance_record_p0_s = struct.Struct(">2H")
fvar_instance_record_op_s = struct.Struct(">H")


class VariationAxisRecord(object):
    def __init__(self, data):
        (
            axis_tag,
            self.min_value,
            self.default_value,
            self.max_value,
            self.flags,
            self.axis_name_id,
        ) = fvar_variation_axis_record_s.unpack(data.read(20))
        self.axis_tag = tag2str(axis_tag)
        self.min_value /= 256
        self.default_value /= 256
        self.max_value /= 256

    def pack(self):
        return fvar_variation_axis_record_s.pack(
            str2tag(self.axis_tag),
            int(self.min_value * 256),
            int(self.default_value * 256),
            int(self.max_value * 256),
            self.flags,
            self.axis_name_id,
        )


class InstanceRecord(object):
    def __init__(self, data, axis_count, instance_size):
        (self.subfamily_name_id, self.flags) = fvar_instance_record_p0_s.unpack(
            data.read(4)
        )
        self.coordinates = [
            i / 256 for i in struct.unpack(f"{axis_count}I", data.read(4 * axis_count))
        ]

        instance_size -= 4 * (axis_count + 1)
        instance_size /= 2
        self.post_script_name_id = None
        if instance_size:
            self.post_script_name_id = fvar_instance_record_op_s.unpack(data.read(2))[0]

    def pack(self):
        return (
            fvar_instance_record_p0_s.pack(self.subfamily_name_id, self.flags)
            + struct.pack(
                f"{len(self.coordinates)}I",
                *[int(coord * 256) for coord in self.coordinates],
            )
            + (
                fvar_instance_record_op_s.pack(self.post_script_name_id)
                if self.post_script_name_id is not None
                else b""
            )
        )


class FontVariationsTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        (
            _,
            _,
            axes_array_offset,
            _,
            axis_count,
            _,
            instance_count,
            instance_size,
        ) = fvar_h_s.unpack(self.data.read(16))
        self.axes = []
        self.data.seek(axes_array_offset)
        for _ in range(axis_count):
            self.axes.append(VariationAxisRecord(self.data))

        instance_size -= axis_count * 4
        self.instances = []
        for _ in range(instance_count):
            self.instances.append(InstanceRecord(self.data, axis_count, instance_size))

        del self.data

    def pack(self):
        instance_size = 4 * len(self.axes)
        instance_size += (
            (4 if self.instances[0].post_script_name_id is None else 6)
            if self.instances
            else 4
        )
        return (
            fvar_h_s.pack(
                1, 0, 16, 2, len(self.axes), 20, len(self.instances), instance_size
            )
            + b"".join(axis.pack() for axis in self.axes)
            + b"".join(instance.pack() for instance in self.instances)
        )

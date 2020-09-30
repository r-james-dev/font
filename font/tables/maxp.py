from .utils import Table
import struct

maxp_v0_5_s = struct.Struct(">IH")
maxp_v1_s = struct.Struct(">13H")


class MaximunProfileTable(Table):
    def __init__(self, *args):
        super().__init__(*args)
        self.version, self.num_glyphs = maxp_v0_5_s.unpack(self.data.read(6))
        self.version /= 65536

        if self.version == 1:
            (
                self.max_points,
                self.max_contours,
                self.max_composite_points,
                self.max_composite_contours,
                self.max_zones,
                self.max_twilight_points,
                self.max_storage,
                self.max_function_defs,
                self.max_instruction_defs,
                self.max_stack_elements,
                self.max_size_of_instructions,
                self.max_component_elements,
                self.max_component_depth,
            ) = maxp_v1_s.unpack(self.data.read(26))

        del self.data

    def pack(self):
        return maxp_v0_5_s.pack(int(self.version * 65536), self.num_glyphs) + (
            maxp_v1_s.pack(
                self.max_points,
                self.max_contours,
                self.max_composite_points,
                self.max_composite_contours,
                self.max_zones,
                self.max_twilight_points,
                self.max_storage,
                self.max_function_defs,
                self.max_instruction_defs,
                self.max_stack_elements,
                self.max_size_of_instructions,
                self.max_component_elements,
                self.max_component_depth,
            )
            if self.version == 1
            else b""
        )

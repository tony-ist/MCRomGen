import sys
from typing import Tuple

import mcschematic


WHITE_GLASS = 'minecraft:white_stained_glass'
REDSTONE_BLOCK = 'minecraft:redstone_block'
ROM_SIZE_BYTES = 256


class MCRomBuilder:
    template: mcschematic.MCSchematic
    result: mcschematic.MCSchematic
    true_block: str
    false_block: str
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    min_z: int
    max_z: int
    least_bit_coords: Tuple[int, int, int]
    second_bit_coords: Tuple[int, int, int]
    most_bit_coords: Tuple[int, int, int]

    def __init__(self, template_path: str, true_block: str = REDSTONE_BLOCK, false_block: str = WHITE_GLASS):
        self.template = mcschematic.MCSchematic(template_path)
        self.result = mcschematic.MCSchematic()
        self.true_block = true_block
        self.false_block = false_block
        bounds = self.template.getStructure().getBounds()
        self.min_x = bounds[0][0]
        self.max_x = bounds[1][0]
        self.min_y = bounds[0][1]
        self.max_y = bounds[1][1]
        self.min_z = bounds[0][2]
        self.max_z = bounds[1][2]

    def write_byte(self, byte: int, address: int):
        if address >= ROM_SIZE_BYTES:
            raise Exception(f'Byte address is {address} but only 0-{ROM_SIZE_BYTES-1} byte addresses are supported')

        x_rows = 8
        y_rows = 8
        z_rows = 32

        x_spacing = (self.max_x - self.min_x) // (x_rows - 1)
        y_spacing = (self.max_y - self.min_y) // (y_rows - 1)
        z_spacing = (self.max_z - self.min_z) // (z_rows - 1)

        print('x,y,z spacing:', x_spacing, y_spacing, z_spacing)

        x = self.min_x + (address // z_rows) * x_spacing
        z = self.min_z + (address % z_rows) * z_spacing

        for i in range(y_rows):
            y = self.min_y + i * y_spacing
            if is_bit_set(byte, i):
                self.result.setBlock((x, y, z), self.true_block)
            else:
                self.result.setBlock((x, y, z), self.false_block)

    def save(self, filename: str):
        if filename.endswith('.schem'):
            filename = filename[0:-6]
        self.result.save(outputFolderPath='', schemName=filename, version=mcschematic.Version.JE_1_18_2)


def inspect_schem(schem_filepath: str, true_block: str = REDSTONE_BLOCK, false_block: str = WHITE_GLASS):
    print('Inspecting schem region...')

    true_blocks_amount = 0
    false_blocks_amount = 0

    schem = mcschematic.MCSchematic(schem_filepath)
    bounds = schem.getStructure().getBounds()
    min_x = bounds[0][0]
    max_x = bounds[1][0]
    min_y = bounds[0][1]
    max_y = bounds[1][1]
    min_z = bounds[0][2]
    max_z = bounds[1][2]
    
    for x in range(min_x, max_x+1):
        for y in range(min_y, max_y+1):
            for z in range(min_z, max_z+1):
                block = schem.getBlockDataAt((x, y, z))
                if block == true_block:
                    true_blocks_amount += 1
                if block == false_block:
                    # print(f'{false_block} at', (x, y, z))
                    false_blocks_amount += 1
    
    print(f'Region min_x, max_x: {min_x}, {max_x}')
    print(f'Region min_y, max_y: {min_y}, {max_y}')
    print(f'Region min_z, max_z: {min_z}, {max_z}')
    print(f'{true_block} amount:', true_blocks_amount)
    print(f'{false_block} amount:', false_blocks_amount)


def is_bit_set(byte: int, bit_address: int) -> bool:
    return (byte >> bit_address) % 2 == 1


def read_csv(csv_filepath: str):
    file_handle = open(csv_filepath, 'r')
    file = file_handle.read()
    bytes_str = file.strip().split(',')
    return list(map(lambda x: int(x), bytes_str))


if __name__ == '__main__':
    filepath = sys.argv[1]
    template_path = sys.argv[2]
    data = read_csv(filepath)

    builder = MCRomBuilder(template_path=template_path)
    builder.least_bit_coords = (157, 80, 184)
    builder.second_bit_coords = (157, 80, 186)
    builder.most_bit_coords = (192, 94, 246)

    for i in range(len(data)):
        builder.write_byte(data[i], i)

    result_path = 'schems/test_rom.schem'
    builder.save(result_path)

    inspect_schem(template_path)
    inspect_schem(result_path)

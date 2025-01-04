import sys
from typing import Dict, List

import mcschematic


WHITE_GLASS = 'minecraft:white_stained_glass'
REDSTONE_BLOCK = 'minecraft:redstone_block'
BLACK_CONCRETE = 'minecraft:black_concrete'
BLUE_WOOL = 'minecraft:blue_wool'
WHITE_WOOL = 'minecraft:white_wool'
GREEN_WOOL = 'minecraft:green_wool'

ROM_SIZE_BYTES = 256


class Coord:
    x: int
    y: int
    z: int

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class MCRomBuilder:
    result: mcschematic.MCSchematic
    true_block: str
    false_block: str
    inner_offsets: List[int]
    outer_offsets: List[int]

    def __init__(self, offsets_path: str, options: Dict[str, str] = None):
        if options is None:
            options = {}

        self.true_block = options.get('true_block', BLACK_CONCRETE)
        self.false_block = options.get('false_block', REDSTONE_BLOCK)

        self.init_offsets(offsets_path)
        self.result = mcschematic.MCSchematic()

    def init_offsets(self, offsets_path: str):
        with open(offsets_path, 'r') as f:
            lines = f.readlines()
            self.inner_offsets = list(map(lambda x: int(x), lines[0].strip().split(' ')))
            self.outer_offsets = list(map(lambda x: int(x), lines[1].strip().split(' ')))

    def write_byte(self, coord: Coord, byte: int):
        y_rows = 8
        y_spacing = 2
        for i in range(y_rows):
            y = coord.y + i * y_spacing
            if is_bit_set(byte, i):
                self.result.setBlock((coord.x, y, coord.z), self.true_block)
            else:
                self.result.setBlock((coord.x, y, coord.z), self.false_block)

    def write_data(self, data: List[int]):
        if len(data) > ROM_SIZE_BYTES:
            raise Exception(f'Data length is {len(data)} but only {ROM_SIZE_BYTES} bytes are supported')

        data_i = 0
        y = -15

        for i in range(len(self.outer_offsets)):
            for j in range(len(self.inner_offsets)):
                # Swap x and z and adjust sign to write bytes in different directions
                x = -self.outer_offsets[j]
                z = -self.inner_offsets[i]
                byte = data[data_i] if data_i < len(data) else 0
                self.write_byte(Coord(x, y, z), byte)
                data_i += 1

    def save(self, filename: str):
        if filename.endswith('.schem'):
            filename = filename[0:-6]
        self.result.save(outputFolderPath='', schemName=filename, version=mcschematic.Version.JE_1_18_2)


def inspect_schem(schem_filepath: str, options: Dict[str, str] = None):
    true_block = options.get('true_block', BLACK_CONCRETE)
    false_block = options.get('false_block', REDSTONE_BLOCK)

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


def read_csv(csv_filepath: str) -> List[int]:
    file_handle = open(csv_filepath, 'r')
    file = file_handle.read()
    bytes_str = file.strip().split(',')
    return list(map(lambda x: int(x), bytes_str))


def read_hex_txt(hex_filepath: str) -> List[int]:
    file_handle = open(hex_filepath, 'r')
    file = file_handle.read()
    bytes_str = file.strip().split(' ')
    return list(map(lambda x: int(x, 16), bytes_str))


def read_bin(bin_filepath: str) -> List[int]:
    file_handle = open(bin_filepath, 'rb')
    file = file_handle.read()
    return list(file)


if __name__ == '__main__':
    data_path = sys.argv[1]
    offsets_path = sys.argv[2]
    result_path = sys.argv[3]
    data = read_bin(data_path)

    options = {
        'true_block': BLACK_CONCRETE,
        'false_block': REDSTONE_BLOCK,
    }

    builder = MCRomBuilder(offsets_path=offsets_path, options=options)

    builder.write_data(data)
    builder.save(result_path)

    print("Inspecting result schematic...")
    inspect_schem(result_path, options=options)

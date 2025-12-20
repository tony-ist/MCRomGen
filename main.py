import sys
from typing import Dict, List

import mcschematic
from dotenv import dotenv_values

env = dotenv_values('.env')

BLOCKS = {
    'WHITE_GLASS': 'minecraft:white_stained_glass',
    'GLASS': 'minecraft:glass',
    'WHITE_CONCRETE': 'minecraft:white_concrete',
    'REDSTONE_BLOCK': 'minecraft:redstone_block',
    'BLACK_CONCRETE': 'minecraft:black_concrete',
    'BLUE_WOOL': 'minecraft:blue_wool',
    'WHITE_WOOL': 'minecraft:white_wool',
    'GREEN_WOOL': 'minecraft:green_wool',
    'BARREL_SS_15': mcschematic.BlockDataDB.BARREL.fromSS(15),
    'BARREL_PREFIX': 'minecraft:barrel[',
}

TRUE_BLOCK = env.get('TRUE_BLOCK') or BLOCKS['BLACK_CONCRETE']
FALSE_BLOCK = env.get('FALSE_BLOCK') or BLOCKS['WHITE_GLASS']
TRUE_BLOCK_INSPECT = env.get('TRUE_BLOCK_INSPECT') or TRUE_BLOCK
FALSE_BLOCK_INSPECT = env.get('FALSE_BLOCK_INSPECT') or FALSE_BLOCK

ROM_SIZE_BYTES = int(env.get('ROM_SIZE_BYTES') or 256)

Y_ROWS = int(env.get('Y_ROWS') or 8)
Y_SPACING = int(env.get('Y_SPACING') or 2)


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
    groups_amount: int
    inner_offsets: List[List[int]]
    outer_offsets: List[List[int]]

    def __init__(self, offsets_path: str):
        self.inner_offsets = []
        self.outer_offsets = []
        self.init_offsets(offsets_path)
        self.result = mcschematic.MCSchematic()

    def init_offsets(self, offsets_path: str):
        with open(offsets_path, 'r') as f:
            lines = f.readlines()
            if len(lines) % 2 != 0:
                raise Exception('Offsets file must have an even number of lines')
            self.groups_amount = len(lines) // 2

            for i in range(self.groups_amount):
                inner_offsets_row = list(map(lambda x: int(x), lines[i * 2].strip().split(' ')))
                outer_offsets_row = list(map(lambda x: int(x), lines[i * 2 + 1].strip().split(' ')))
                self.inner_offsets.append(inner_offsets_row)
                self.outer_offsets.append(outer_offsets_row)

    def write_byte(self, coord: Coord, byte: int):
        for i in range(Y_ROWS):
            y = coord.y + i * Y_SPACING
            if is_bit_set(byte, i):
                self.result.setBlock((coord.x, y, coord.z), TRUE_BLOCK)
            else:
                self.result.setBlock((coord.x, y, coord.z), FALSE_BLOCK)

    def write_data(self, data: List[int]):
        if len(data) > ROM_SIZE_BYTES:
            raise Exception(f'Data length is {len(data)} but only {ROM_SIZE_BYTES} bytes are supported')

        data_i = 0
        y = -(Y_ROWS * Y_SPACING) + 1

        for group in range(self.groups_amount):
            for i in range(len(self.outer_offsets[group])):
                for j in range(len(self.inner_offsets[group])):
                    x = self.outer_offsets[group][i]
                    z = self.inner_offsets[group][j]
                    byte = data[data_i] if data_i < len(data) else 0
                    self.write_byte(Coord(x, y, z), byte)
                    data_i += 1

    def save(self, filename: str):
        if filename.endswith('.schem'):
            filename = filename[0:-6]
        self.result.save(outputFolderPath='', schemName=filename, version=mcschematic.Version.JE_1_18_2)


def inspect_schem(schem_filepath: str):
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
                if block.startswith(TRUE_BLOCK_INSPECT):
                    true_blocks_amount += 1
                if block.startswith(FALSE_BLOCK_INSPECT):
                    # print(f'{false_block} at', (x, y, z))
                    false_blocks_amount += 1
    
    print(f'Region min_x, max_x: {min_x}, {max_x}')
    print(f'Region min_y, max_y: {min_y}, {max_y}')
    print(f'Region min_z, max_z: {min_z}, {max_z}')
    print(f'{TRUE_BLOCK_INSPECT} amount:', true_blocks_amount)
    print(f'{FALSE_BLOCK_INSPECT} amount:', false_blocks_amount)


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
    bytes_str = file.strip().split()
    return list(map(lambda x: int(x, 16), bytes_str))


def read_bin(bin_filepath: str) -> List[int]:
    file_handle = open(bin_filepath, 'rb')
    file = file_handle.read()
    return list(file)


if __name__ == '__main__':
    data_path = sys.argv[1]
    offsets_path = sys.argv[2]
    result_path = sys.argv[3]
    data = read_hex_txt(data_path)

    builder = MCRomBuilder(offsets_path=offsets_path)

    builder.write_data(data)
    builder.save(result_path)

    print("Inspecting result schematic...")
    inspect_schem(result_path)

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


class Vector:
    x: int
    y: int
    z: int

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Coord:
    x: int
    y: int
    z: int

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def add(self, vector: Vector):
        return Coord(self.x + vector.x, self.y + vector.y, self.z + vector.z)


class MCRomBuilder:
    template: mcschematic.MCSchematic
    result: mcschematic.MCSchematic
    true_block: str
    false_block: str
    start_block: str
    end_block: str
    second_block: str
    bounds_from: Coord
    bounds_to: Coord

    def __init__(self, template_path: str, options: Dict[str, str] = None):
        if options is None:
            options = {}

        self.true_block = options.get('true_block', BLACK_CONCRETE)
        self.false_block = options.get('false_block', REDSTONE_BLOCK)
        self.start_block = options.get('start_block', WHITE_WOOL)
        self.end_block = options.get('end_block', BLUE_WOOL)
        self.second_block = options.get('second_block', GREEN_WOOL)

        self.template = mcschematic.MCSchematic(template_path)
        self.result = mcschematic.MCSchematic()
        bounds = self.template.getStructure().getBounds()

        print(f'Bounds: {bounds}')

        self.bounds_from = Coord(bounds[0][0], bounds[0][1], bounds[0][2])
        self.bounds_to = Coord(bounds[1][0], bounds[1][1], bounds[1][2])

        self.start_block_coord = self.find_block(self.start_block)
        self.second_block_coord = self.find_block(self.second_block)
        self.end_block_coord = self.find_block(self.end_block)

    def find_block(self, block: str) -> Coord:
        pass # TODO Implement

    def write_byte2(self, byte: int, address: int):
        if address >= ROM_SIZE_BYTES:
            raise Exception(f'Byte address is {address} but only 0-{ROM_SIZE_BYTES-1} byte addresses are supported')

        x_rows = 8
        y_rows = 8
        z_rows = 32

        x_spacing = (self.bounds_to.x - self.bounds_from.x) // (x_rows - 1)
        y_spacing = (self.bounds_to.y - self.bounds_from.y) // (y_rows - 1)
        z_spacing = (self.bounds_to.z - self.bounds_from.z) // (z_rows - 1)

        print('x,y,z spacing:', x_spacing, y_spacing, z_spacing)

        x = self.bounds_from.x + (address // z_rows) * x_spacing
        z = self.bounds_from.z + (address % z_rows) * z_spacing

        for i in range(y_rows):
            y = self.bounds_from.y + i * y_spacing
            if is_bit_set(byte, i):
                self.result.setBlock((x, y, z), self.true_block)
            else:
                self.result.setBlock((x, y, z), self.false_block)

    def write_byte(self, byte: int, coord: Coord):
        y_rows = 8
        y_spacing = 2
        for i in range(y_rows):
            y = coord.y + i * y_spacing
            if is_bit_set(byte, i):
                self.result.setBlock((coord.x, y, coord.z), self.true_block)
            else:
                self.result.setBlock((coord.x, y, coord.z), self.false_block)

    def is_byte(self, coord: Coord) -> bool:
        return self.template_at(coord) == self.false_block

    def template_at(self, coord: Coord) -> str:
        return self.template.getStructure().getBlockDataAt((coord.x, coord.y, coord.z))

    def write_data(self, data: List[int]):
        x_size = abs(self.bounds_to.x - self.bounds_from.x)
        z_size = abs(self.bounds_to.z - self.bounds_from.z)

        data_i = 0

        for i in range(x_size):
            for j in range(z_size):
                coord = Coord(i, j, 0)
                if self.is_byte(coord):
                    self.write_byte(data[data_i], coord)
                    data_i += 1


    def save(self, filename: str):
        if filename.endswith('.schem'):
            filename = filename[0:-6]
        self.result.save(outputFolderPath='', schemName=filename, version=mcschematic.Version.JE_1_18_2)


def inspect_schem(schem_filepath: str, options: Dict[str, str] = None):
    true_block = options.get('true_block', BLACK_CONCRETE)
    false_block = options.get('false_block', REDSTONE_BLOCK)
    start_block = options.get('start_block', WHITE_WOOL)
    end_block = options.get('end_block', BLUE_WOOL)
    second_block = options.get('second_block', GREEN_WOOL)

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


def read_hex(hex_filepath: str) -> List[int]:
    file_handle = open(hex_filepath, 'r')
    file = file_handle.read()
    bytes_str = file.strip().split(' ')
    return list(map(lambda x: int(x, 16), bytes_str))


if __name__ == '__main__':
    data_path = sys.argv[1]
    template_path = sys.argv[2]
    result_path = sys.argv[3]
    data = read_hex(data_path)

    options = {
        'true_block': BLACK_CONCRETE,
        'false_block': REDSTONE_BLOCK,
        'start_block': WHITE_WOOL,
        'end_block': BLUE_WOOL,
        'second_block': GREEN_WOOL,
    }

    builder = MCRomBuilder(template_path=template_path, options=options)

    builder.write_data(data)
    builder.save(result_path)

    print("Inspecting template schematic...")
    inspect_schem(template_path, options=options)
    print("Inspecting result schematic...")
    inspect_schem(result_path, options=options)

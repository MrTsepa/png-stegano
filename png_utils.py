import binascii

import struct

PNG_START_BYTES = bytearray((137, 80, 78, 71, 13, 10, 26, 10))
PNG_START_BYTES_LEN = 8


class Chunk:
    def __init__(self, length, type, data, crc=None):
        self.length = length
        self.type = type
        self.data = data
        self.crc = crc if crc is not None else self.calculate_crc()

    def calculate_crc(self):
        return binascii.crc32(self.type + self.data)

    @property
    def total_length(self):
        return 4 + 4 + self.length + 4

    @staticmethod
    def from_bytes(buffer, pos):
        cur_pos = pos

        length, = struct.unpack('>I', buffer[cur_pos:cur_pos + 4])
        cur_pos += 4

        chunk_type = buffer[cur_pos:cur_pos + 4]
        cur_pos += 4

        data = buffer[cur_pos:cur_pos + length]
        cur_pos += length

        crc, = struct.unpack('>I', buffer[cur_pos:cur_pos + 4])
        cur_pos += 4

        return Chunk(length, chunk_type, data, crc)

    def to_bytes(self):
        length_bytes = struct.pack('>I', self.length)
        crc_bytes = struct.pack('>I', self.crc)
        return length_bytes + self.type + self.data + crc_bytes

    def __str__(self):
            return 'Type: {}, length: {}, data: {}, crc: {}, calculated crc: {}'.\
                format(self.type, self.length, self.data if self.length <= 15 else self.data[:15] + b'...',
                       self.crc, self.calculate_crc())


def print_png_chunks(png_bytes):
    """prints all chunks of png, format is defined in Chunk.__str__"""
    assert png_bytes[:PNG_START_BYTES_LEN] == PNG_START_BYTES, 'Invalid PNG'

    cur_pos = PNG_START_BYTES_LEN
    while True:
        chunk = Chunk.from_bytes(png_bytes, cur_pos)
        cur_pos += chunk.total_length
        print(chunk)

        if chunk.type == b'IEND':
            break


def get_png_size(png_bytes):
    """:returns width, height"""
    assert png_bytes[:PNG_START_BYTES_LEN] == PNG_START_BYTES, 'Invalid PNG'
    ihdr = get_chunk_data(png_bytes, b'IHDR')
    return struct.unpack('!II', ihdr[:8])


def get_png_color_flags(png_bytes):
    assert png_bytes[:PNG_START_BYTES_LEN] == PNG_START_BYTES, 'Invalid PNG'
    ihdr = get_chunk_data(png_bytes, b'IHDR')
    b = struct.unpack('b', ihdr[9:10])[0]
    flags = {
        'IS_ALPHA_USED': b & 0b100 != 0,
        'IS_COLOR_USED': b & 0b010 != 0,
        'IS_PALETTE_USED': b & 0b001 != 0
    }
    return flags


def get_pixel_size(color_flags):
    """:return bytes per pixel"""
    pixel_size = 3 if color_flags['IS_COLOR_USED'] else 1
    pixel_size += 1 if color_flags['IS_ALPHA_USED'] else 0
    return pixel_size


def get_chunk_data(png_bytes, chunk_type):
    """:return data bytes of chunk with given type or None"""
    assert png_bytes[:PNG_START_BYTES_LEN] == PNG_START_BYTES, 'Invalid PNG'

    cur_pos = PNG_START_BYTES_LEN
    while True:
        chunk = Chunk.from_bytes(png_bytes, cur_pos)
        cur_pos += chunk.total_length

        if chunk.type == chunk_type:
            return chunk.data

        if chunk.type == b'IEND':
            break


def add_chunk_data(png_bytes, chunk_type, data_bytes):
    """
    add chunk with given type and data after IHDR chunk
    :return new png as bytes
    """
    assert png_bytes[:PNG_START_BYTES_LEN] == PNG_START_BYTES, 'Invalid PNG'
    res_bytes = b''
    res_bytes += PNG_START_BYTES

    data_chunk = Chunk(len(data_bytes), chunk_type, data_bytes).to_bytes()
    cur_pos = PNG_START_BYTES_LEN
    while True:
        chunk = Chunk.from_bytes(png_bytes, cur_pos)
        cur_pos += chunk.total_length
        res_bytes += chunk.to_bytes()

        if chunk.type == b'IHDR':
            res_bytes += data_chunk

        if chunk.type == b'IEND':
            break

    return res_bytes


def set_chunk_data(png_bytes, chunk_type, data_bytes):
    """
    change data field of chunk with given type
    :return new png as bytes
    """
    assert png_bytes[:PNG_START_BYTES_LEN] == PNG_START_BYTES, 'Invalid PNG'
    res_bytes = b''
    res_bytes += PNG_START_BYTES

    data_chunk = Chunk(len(data_bytes), chunk_type, data_bytes).to_bytes()
    cur_pos = PNG_START_BYTES_LEN
    while True:
        chunk = Chunk.from_bytes(png_bytes, cur_pos)
        cur_pos += chunk.total_length
        if chunk.type == chunk_type:
            res_bytes += data_chunk
            continue
        res_bytes += chunk.to_bytes()

        if chunk.type == b'IEND':
            break

    return res_bytes
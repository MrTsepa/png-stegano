import struct

PNG_START_BYTES = bytes((137, 80, 78, 71, 13, 10, 26, 10))


class Chunk:
    def __init__(self, length, type, data, crc=None):
        self.length = length
        self.type = type
        self.data = data
        self.crc = crc if crc is not None else self.calculate_crc()

    def calculate_crc(self):
        return 0

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
            return 'Type: {}, length: {}, data: {}, crc: {}'.\
                format(self.type, self.length, self.data if self.length <= 15 else self.data[:15] + b'...', self.crc)


def print_png_chunks(png_bytes):
    assert png_bytes[:8] == PNG_START_BYTES, 'Invalid PNG'

    cur_pos = 8
    while True:
        chunk = Chunk.from_bytes(png_bytes, cur_pos)
        cur_pos += chunk.total_length
        print(chunk)

        if chunk.type == b'IEND':
            break


def hide_data_in_png(png_bytes, data_bytes, chunk_type='steg'):
    assert png_bytes[:8] == PNG_START_BYTES, 'Invalid PNG'
    res_bytes = PNG_START_BYTES

    data_chunk = Chunk(len(data_bytes), bytes(chunk_type, 'utf8'), data_bytes).to_bytes()
    cur_pos = 8
    while True:
        chunk = Chunk.from_bytes(png_bytes, cur_pos)
        cur_pos += chunk.total_length
        res_bytes += chunk.to_bytes()

        if chunk.type == b'IHDR':
            res_bytes += data_chunk

        if chunk.type == b'IEND':
            break

    return res_bytes


def get_data_from_png(png_bytes, chunk_type='steg'):
    assert png_bytes[:8] == PNG_START_BYTES, 'Invalid PNG'

    cur_pos = 8
    while True:
        chunk = Chunk.from_bytes(png_bytes, cur_pos)
        cur_pos += chunk.total_length

        if chunk.type == bytes(chunk_type, 'utf8'):
            return chunk.data

        if chunk.type == b'IEND':
            break


if __name__ == '__main__':
    with open('image.png', 'rb') as f:
        buffer = f.read()

    print_png_chunks(buffer)
    print()
    buffer_with_data = hide_data_in_png(buffer, b'Hello, World')
    print_png_chunks(buffer_with_data)

    print(get_data_from_png(buffer_with_data))

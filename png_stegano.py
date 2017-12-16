import random
import zlib

from filter_utils import reconstruct_scanline, FILTER, filter_scanline
from png_utils import *


KEY = 1093212


class PngSteganographer:
    def hide(self, buffer, data_bytes):
        raise NotImplementedError

    def get(self, buffer):
        raise NotImplementedError


class SimpleSteganographer(PngSteganographer):
    """
    Simply inserts additional chunk after IHDR.
    All chunk_type letters should be lowercase
    to show png decoder to pass over this chunk,
    otherwise behaviour of decoder is undefined.
    """

    def hide(self, png_bytes, data_bytes, chunk_type=b'steg'):
        return add_chunk_data(png_bytes, chunk_type, data_bytes)

    def get(self, png_bytes, chunk_type=b'steg'):
        return get_chunk_data(png_bytes, chunk_type)


class FilterSteganographer(PngSteganographer):

    def get(self, png_buffer):
        """
        :return decoded bytes
        """

        idat = get_chunk_data(png_buffer, b'IDAT')
        decompressed = zlib.decompress(idat)
        size = get_png_size(png_buffer)

        print("length of IDAT: {} bytes".format(len(idat)))
        print("length of decompressed: {} bytes".format(len(zlib.decompress(idat))))
        print("image size:", size)

        color_flags = get_png_color_flags(png_buffer)
        pixel_size = get_pixel_size(color_flags)
        line_size = size[0] * pixel_size + 1

        filter_bits = []
        for i in range(0, len(decompressed), line_size):
            filter_bits.append(decompressed[i])

        print('filter bits found: ', ''.join(str(bit) for bit in filter_bits))

        random.seed(KEY)
        samapled_positions = random.sample(range(size[1]), size[1])

        print(samapled_positions)
        bits_positioned = list(map(lambda p: filter_bits[p], samapled_positions))
        # bits = ''.join(str(bit) for bit in filter_bits if bit < 2)
        bits = ''.join(str(bit) for bit in bits_positioned if bit < 2)
        print(bits)
        bits = bits[:len(bits) - len(bits) % 8]
        if not bits:
            bits = '0'
        n = int(bits, base=2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big')

    def hide(self, png_buffer, data_bytes):
        """
        :return: new png as bytes
        """

        idat = get_chunk_data(png_buffer, b'IDAT')
        decompressed = zlib.decompress(idat)
        size = get_png_size(png_buffer)

        bin_data = []  # array of 0, 1
        for byte in data_bytes:
            for c in '{:08b}'.format(byte):
                bin_data.append(int(c))

        assert len(bin_data) <= size[1], 'Too much data'

        print("length of IDAT: {} bytes".format(len(idat)))
        print("length of decompressed: {} bytes".format(len(zlib.decompress(idat))))
        print("image size:", size)

        color_flags = get_png_color_flags(png_buffer)
        pixel_size = get_pixel_size(color_flags)
        line_size = size[0] * pixel_size + 1

        scanlines = []
        filter_bits = []
        for i in range(0, len(decompressed), line_size):
            filter_bits.append(decompressed[i])
            scanlines.append(decompressed[i + 1:i + line_size])

        new_filter_bits = filter_bits[:]

        random.seed(KEY)
        samapled_positions = random.sample(range(size[1]), size[1])[:len(bin_data)]
        print(samapled_positions)
        print(''.join([str(x) for x in bin_data]))

        for i, p in enumerate(samapled_positions):
            new_filter_bits[p] = bin_data[i]

        for i, p in enumerate(sorted(samapled_positions)):
            rec_scanline = reconstruct_scanline(
                FILTER[filter_bits[p]], scanlines[p], scanlines[p - 1] if p > 0 else None, pixel_size)
            filtered_scanline = filter_scanline(
                FILTER[new_filter_bits[p]], rec_scanline, scanlines[p - 1] if p > 0 else None, pixel_size)
            scanlines[p] = filtered_scanline[:]

        filtered_scanlines = scanlines

        new_idat_decompressed = bytearray()
        for i in range(len(filtered_scanlines)):
            new_idat_decompressed.append(new_filter_bits[i])
            new_idat_decompressed.extend(filtered_scanlines[i])

        new_idat_data = zlib.compress(new_idat_decompressed)
        res = set_chunk_data(png_buffer, b'IDAT', new_idat_data)
        return res

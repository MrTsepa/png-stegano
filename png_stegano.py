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

    def get(self, png_buffer, key=None):
        """
        :return decoded bytes
        """

        if not key:
            key = KEY

        idat = get_chunk_data(png_buffer, b'IDAT')
        decompressed = zlib.decompress(idat)
        size = get_png_size(png_buffer)

        print("length of IDAT: {} bytes".format(len(idat)))
        print("length of decompressed: {} bytes".format(len(zlib.decompress(idat))))
        print("image size:", size)

        color_flags = get_png_color_flags(png_buffer)
        pixel_size = get_pixel_size(color_flags)
        line_size = size[0] * pixel_size + 1

        filter_bytes = []
        for i in range(0, len(decompressed), line_size):
            filter_bytes.append(decompressed[i])

        print('filter bytes: ', ''.join(str(byte) for byte in filter_bytes))

        random.seed(key)
        samapled_positions = random.sample(range(size[1]), size[1])
        print('positions:', ' '.join(map(str, samapled_positions)))

        bytes_positioned = list(map(lambda p: filter_bytes[p], samapled_positions))
        bytes = ''.join(str(byte) for byte in bytes_positioned if byte < 2)
        print('bytes on positions', bytes)
        bytes = bytes[:len(bytes) - len(bytes) % 8]
        if not bytes:
            bytes = '0'
        n = int(bytes, base=2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big')

    def hide(self, png_buffer, data_bytes, key=None):
        """
        :return: new png as bytes
        """

        if not key:
            key = KEY

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
        filter_bytes = []
        for i in range(0, len(decompressed), line_size):
            filter_bytes.append(decompressed[i])
            scanlines.append(decompressed[i + 1:i + line_size])

        reconstructed_scanlines = []
        for p in range(len(scanlines)):
            reconstructed_scanline = reconstruct_scanline(
                FILTER[filter_bytes[p]],
                scanlines[p],
                reconstructed_scanlines[p - 1] if p > 0 else None,
                pixel_size
            )
            reconstructed_scanlines.append(reconstructed_scanline)

        new_filter_bytes = filter_bytes[:]

        random.seed(key)
        sampled_positions = random.sample(range(size[1]), size[1])[:len(bin_data)]
        print('positions:', ' '.join(map(str, sampled_positions)))
        print('bin data:', ''.join([str(x) for x in bin_data]))

        for i, p in enumerate(sampled_positions):
            new_filter_bytes[p] = bin_data[i]

        filtered_scanlines = []
        for p in range(len(reconstructed_scanlines)):
            filtered_scanline = filter_scanline(
                FILTER[new_filter_bytes[p]],
                reconstructed_scanlines[p],
                reconstructed_scanlines[p - 1] if p > 0 else None,
                pixel_size
            )
            filtered_scanlines.append(filtered_scanline)
        # for i, p in enumerate(sorted(samapled_positions)):
        #     rec_scanline = reconstruct_scanline(
        #         FILTER[filter_bits[p]], scanlines[p], scanlines[p - 1] if p > 0 else None, pixel_size)
        #     filtered_scanline = filter_scanline(
        #         FILTER[new_filter_bits[p]], rec_scanline, scanlines[p - 1] if p > 0 else None, pixel_size)
        #     scanlines[p] = filtered_scanline[:]

        new_idat_decompressed = bytearray()
        for i in range(len(filtered_scanlines)):
            new_idat_decompressed.append(new_filter_bytes[i])
            new_idat_decompressed.extend(filtered_scanlines[i])

        new_idat_data = zlib.compress(new_idat_decompressed)
        res = set_chunk_data(png_buffer, b'IDAT', new_idat_data)
        return res

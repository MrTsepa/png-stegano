import zlib

from filter_utils import reconstruct_scanline, FILTER, filter_scanline
from png_utils import *


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
        Joins all filter bits which are 0 or 1, then decodes this bit sequence to bytes
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

        print('filter bits found: ', ''.join(str(bit) for bit in filter_bits if bit < 2))

        bits = ''.join(str(bit) for bit in filter_bits if bit < 2)
        if not bits:
            bits = '0'
        n = int(bits, base=2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big')

    def hide(self, png_buffer, data_bytes):
        """
        Firstly represents data_bytes as bit sequence,
        then for each line of first `len(bits)` reconstructs line if it already has filter
        and applies filter None or Sub (0 or 1). As a result binary data is hidden in filter bytes.
        :return: new png as bytes
        """

        idat = get_chunk_data(png_buffer, b'IDAT')
        decompressed = zlib.decompress(idat)
        size = get_png_size(png_buffer)

        bin_data = []  # array of 0, 1

        for c in bin(int.from_bytes(data_bytes, 'big')).lstrip('0b'):
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

        reconstructed_scanlines = []
        for i in range(len(scanlines)):
            reconstructed_scanlines.append(reconstruct_scanline(
                FILTER[filter_bits[i]], scanlines[i], reconstructed_scanlines[i-1] if i > 0 else None, pixel_size))

        filtered_scanlines = []
        for i in range(len(scanlines)):
            filtered_scanlines.append(filter_scanline(
                FILTER[bin_data[i] if i < len(bin_data) else 2],
                reconstructed_scanlines[i],
                reconstructed_scanlines[i-1] if i > 0 else None,
                pixel_size
            ))

        new_idat_decompressed = bytearray()
        for i in range(len(filtered_scanlines)):
            new_idat_decompressed.append(bin_data[i] if i < len(bin_data) else 2)
            new_idat_decompressed.extend(filtered_scanlines[i])

        new_idat_data = zlib.compress(new_idat_decompressed)
        res = set_chunk_data(png_buffer, b'IDAT', new_idat_data)
        return res

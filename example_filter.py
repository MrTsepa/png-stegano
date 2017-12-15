from png_stegano import *

with open('image.png', 'rb') as f:
    png_buffer = f.read()

steg = FilterSteganographer()
print(get_png_color_flags(png_buffer))
print(steg.get(png_buffer))

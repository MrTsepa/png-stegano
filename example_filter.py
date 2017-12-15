from png_stegano import *

with open('image.png', 'rb') as f:
    png_buffer = f.read()

steg = FilterSteganographer()
png_with_data = steg.hide(png_buffer, b'hel')
with open('image_with_data.png', 'wb') as f:
    f.write(png_with_data)


with open('image_with_data.png', 'rb') as f:
    png_buffer = f.read()
print(FilterSteganographer().get(png_buffer))

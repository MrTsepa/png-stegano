from png_stegano import *

input_filename = 'images/small_image.png'
output_filename = 'images/small_image_with_data.png'

with open(input_filename, 'rb') as f:
    png_buffer = f.read()

steg = FilterSteganographer()
png_with_data = steg.hide(png_buffer, b'hel')
with open(output_filename, 'wb') as f:
    f.write(png_with_data)


with open(output_filename, 'rb') as f:
    png_buffer = f.read()
print(FilterSteganographer().get(png_buffer))

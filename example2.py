from png_stegano import hide_data_in_png, print_png_chunks

with open('image.png', 'rb') as f:
    buffer = f.read()

print_png_chunks(buffer)
print()

buffer_with_data = hide_data_in_png(buffer, b'Hello, World')
print_png_chunks(buffer_with_data)

with open('image_with_data.png', 'wb') as f:
    f.write(buffer_with_data)

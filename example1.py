from png_stegano import print_png_chunks

with open('image.png', 'rb') as f:
    buffer = f.read()

print_png_chunks(buffer)

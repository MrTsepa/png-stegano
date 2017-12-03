from png_stegano import print_png_chunks, get_data_from_png

with open('image_with_data.png', 'rb') as f:
    buffer = f.read()

print_png_chunks(buffer)
print()

data = get_data_from_png(buffer)

if data:
    print('Hidden data: {}'.format(data))
else:
    print('No data found')

from guizero import App, Text, PushButton, TextBox, Box, error
from tkinter.filedialog import askopenfilename, asksaveasfile

from png_stegano import FilterSteganographer

import string

input_path = None
buffer = None


def choose_file():
    global input_path, buffer
    input_path = askopenfilename(
        filetypes=(("PNG images", "*.png"), ("All Files", "*.*")),
        title="Choose image"
    )
    input_path_widget.set_text(input_path)
    with open(input_path, 'rb') as f:
        buffer = f.read()

    hidden_data = FilterSteganographer().get(buffer)
    hidden_data_text.set("Hidden data found: ")
    if hidden_data and any(chr(byte) in string.printable for byte in hidden_data):
        hidden_data_red_text.set(hidden_data)
    else:    
        hidden_data_red_text.set('No data')


def save_file():
    if not buffer:
        error('Error', 'No file loaded!')
        return
    try:
        buffer_with_data = FilterSteganographer().hide(buffer, bytes(text_box_secret.get(), encoding='utf8'))
    except AssertionError as e:
        error('Error', e)
        return
    f = asksaveasfile(mode='wb', defaultextension=".png")
    if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    f.write(buffer_with_data)
    f.close()


app = App(title="Hello world", layout='auto', height=150)
vertical_box = Box(app, layout='grid')
horizontal_box0 = Box(vertical_box, layout='grid', grid=(0, 0))
horizontal_box1 = Box(vertical_box, layout='grid', grid=(1, 0))
horizontal_box2 = Box(vertical_box, layout='grid', grid=(2, 0))
horizontal_box3 = Box(vertical_box, layout='grid', grid=(3, 0))
horizontal_box4 = Box(vertical_box, layout='grid', grid=(4, 0))

input_path_widget = PushButton(
    horizontal_box0,
    text="Choose file...",
    command=choose_file,
    grid=(0, 0),
)

message_secret = Text(horizontal_box1, "Secret message: ", grid=(0, 0))
text_box_secret = TextBox(horizontal_box1, text='', width=20, grid=(0, 1))
save_file_widget = PushButton(
    horizontal_box1,
    text="Save stego-file...",
    command=save_file,
    grid=(0, 2)
)

hidden_data_text = Text(horizontal_box2, "", grid=(0, 0))
hidden_data_red_text = Text(horizontal_box2, "", grid=(0, 1), color='red')

app.display()

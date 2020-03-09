import glob
from PIL import Image


def calcuate_size(files):
    size_x = []
    size_y = []

    for file in files:
        image = Image.open(file)
        size_x.append(image.size[0])
        size_y.append(image.size[1])

    x_min = min(size_x)
    y_min = min(size_y)
    total_x_size = x_min * len(files)

    return x_min, y_min, total_x_size

def resize_to_min(files, x_min, y_min, x_size):
    file_list = []

    for file in files:
        image = Image.open(file)
        resized_file = image.resize((x_min, y_min))
        file_list.append(resized_file)

    return file_list, x_size, x_min, y_min

def image_merge(file_list, x_size, x_min, y_min):
    new_image = Image.new('RGB', (x_size, y_min), (256, 256, 256))

    for i in range(len(file_list)):
        area = ((i * x_min), 0, (x_min * (i+1)), y_min)
        new_image.paste(file_list[i], area)
    # new_image.save('result.png', 'png')

target_dir = './images/'
files = glob.glob(target_dir + '*.*')

x_min, y_min, x_size = calcuate_size(files)

file_list, x_size, x_min, y_min = resize_to_min(files, x_min, y_min, x_size)

image_merge(file_list, x_size, x_min, y_min)

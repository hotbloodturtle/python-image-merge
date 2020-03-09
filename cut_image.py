import os
import random
import string
import glob
from PIL import Image

# 위아래로 100px씩 잘라내는 스크립트

cut_dir = '../photo/reference/cut/'
if not os.path.exists(result_dir):
    os.makedirs(result_dir)
files = glob.glob(face_dir + '*.*')

result_dir = f'../photo/reference/cut_result/'
if not os.path.exists(result_dir):
    os.makedirs(result_dir)
for file in files:
    image = Image.open(file)
    w, h = image.size
    filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    area = (0, 100, w, h-100)
    cropped_img = image.crop(area)
    cropped_img.save(f'{result_dir}{filename}.png', 'png')

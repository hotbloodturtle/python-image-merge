import os
import random
import string
import glob
from PIL import Image


# change_num 값을 기준값(starndard)으로 지정
# 이후 증가된 change_num값의 비율만큼 scale_change_num값도 증가
# ex)
# x = 500, y = 750 에서 y를 1500으로 변경하고 싶다
# y, x = same_scale_resize(1500, y, x)
# y가 1500으로 증가한 비율만큼 x값도 증가함
def same_scale_resize(standard, change_num, scale_change_num):
    standard = standard + 100
    diff_scale = change_num/(standard - change_num)
    change_num = standard
    scale_change_num = round(scale_change_num + (scale_change_num/diff_scale))
    return change_num, scale_change_num


def image_merge(face_image, ref_image):
    face_x, face_y = face_image.size[0], face_image.size[1]
    ref_x, ref_y = ref_image.size[0], ref_image.size[1]

    if face_x > ref_x:
        ref_y, ref_x = same_scale_resize((face_y-200), ref_y, ref_x)
        ref_image = ref_image.resize((ref_x, ref_y))
    else:
        face_y, face_x = same_scale_resize(ref_y, face_y, face_x)
        face_image = face_image.resize((face_x, face_y))

    total_x = face_x + ref_x + 30
    y_max = max([face_y, ref_y])

    new_image = Image.new('RGB', (total_x, y_max), (256, 256, 256))

    between_y_value = abs(face_y - ref_y)
    start_y = round(between_y_value/2)
    if face_y > ref_y:
        face_area = (0, 0, face_x, face_y)
        ref_area = (face_x+30, start_y, face_x+ref_x+30, start_y+ref_y)
    else:
        face_area = (0, start_y, face_x, start_y+face_y)
        ref_area = (face_x+30, 0, face_x+ref_x+30, ref_y)

    new_image.paste(face_image, face_area)
    new_image.paste(ref_image, ref_area)
    return new_image


def iter_frames(im):
    try:
        i= 0
        while 1:
            im.seek(i)
            imframe = im.copy()
            if i == 0:
                palette = imframe.getpalette()
            else:
                imframe.putpalette(palette)
            yield imframe
            i += 1
    except EOFError:
        pass


face_dir = '../photo/reference/face/'
face_files = glob.glob(face_dir + '*.*')

ref_dir = '../photo/reference/reference/'
ref_files = glob.glob(ref_dir + '*.*')

face_len = len(face_files)
ref_len = len(ref_files)
min_len = min([face_len, ref_len])

face_ran = [i for i in range(face_len)]
random.shuffle(face_ran)
face_ran = face_ran[:min_len]

ref_ran = [i for i in range(ref_len)]
random.shuffle(ref_ran)
ref_ran = ref_ran[:min_len]

merge_dir = f'../photo/merged/'
if not os.path.exists(merge_dir):
    os.makedirs(merge_dir)

print(min_len)
for i in range(min_len):
    print(i)
    face_i = face_ran[i]
    ref_i = ref_ran[i]

    face_file = face_files[face_i]
    ref_file = ref_files[ref_i]
    face_image = Image.open(face_file)
    ref_image = Image.open(ref_file)

    filename = ''.join(random.choices(string.ascii_uppercase + string.digits,
                                      k=10))
    if '.gif' in ref_file:
        merged_images = []

        for i, ref_frame in enumerate(iter_frames(ref_image)):
            merged_image = image_merge(face_image, ref_frame)
            merged_images.append(merged_image)

        merged_images[0].save(
            f'{merge_dir}{filename}.gif',
            save_all=True,
            append_images=merged_images[1:],
            duration=100,loop=0
        )
    else:
        merged_image = image_merge(face_image, ref_image)
        merged_image.save(f'{merge_dir}{filename}.png', 'png')

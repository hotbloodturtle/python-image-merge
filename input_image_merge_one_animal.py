import os
import sys
import shutil
import glob
import math
from PIL import Image

from functions import (
    get_min_len_and_random_list, create_file_name, iter_frames,
    same_scale_resize_height, image_merge_to_width_center,
)

# 상수 설정
GIF_WIDTH = 300
GIF_HEIGHT = 550
GIF_MARGIN = 10

IMAGE_WIDTH = 900
IMAGE_HEIGHT = 900
IMAGE_MARGIN = 30

MAX_MERGE_LENGTH = 100

ANI_DIR = '../photo/reference/animal/'
CHAR_DIR = '../photo/reference/character/'
MERGE_DIR = '../photo/merged/'


# 합성 이미지 폴더 생성
if not os.path.exists(MERGE_DIR):
    os.makedirs(MERGE_DIR)

# 동물사진 폴더별로 종류 지정 (미입력 시 모든 폴더의 파일 지정)
ani_folder = input('동물폴더이름: ')

if not ani_folder:
    ani_folders = glob.glob(ANI_DIR + '*/')
else:
    ani_folders = []
    ani_names = ani_folder.split(' ')
    for ani_name in ani_names:
        ani_folders += glob.glob(ANI_DIR + f'{ani_name}/')

ani_ext = input('동물사진 확장자: ')
char_ext = input('캐릭터사진 확장자: ')

ani_ext = ani_ext if ani_ext else '*'
char_ext = char_ext if char_ext else '*'

# 대상 이미지들 string 값으로 list 화/
ani_files = []
for ani_folder in ani_folders:
    ani_files += glob.glob(ani_folder + f'*.{ani_ext}')

char_files = glob.glob(CHAR_DIR + f'*.{char_ext}')

# 반복횟수, 랜덤 리스트 get
min_len, ani_ran, char_ran = get_min_len_and_random_list(ani_files, char_files)

# 최대 회수 지정
if min_len > MAX_MERGE_LENGTH:
    min_len = MAX_MERGE_LENGTH

# 이미지 합성
print(f'total count: {min_len}')
for i in range(min_len):
    print(i)

    # 파일 이름(string)
    ani_file = ani_files[ani_ran[i]]
    char_file = char_files[char_ran[i]]

    # pillow image
    ani_image = Image.open(ani_file)
    char_image = Image.open(char_file)

    # 파일이름 랜덤 get
    file_name = create_file_name()

    if not '.gif' in ani_file and not '.gif' in char_file:
        ani_image = same_scale_resize_height(IMAGE_HEIGHT, ani_image)
        char_image = same_scale_resize_height(IMAGE_HEIGHT-100, char_image)
        merged_image = image_merge_to_width_center(ani_image, char_image,
                                                   IMAGE_MARGIN)
        merged_image.save(f'{MERGE_DIR}{file_name}.png', 'png')
        continue

    # 캐릭터사진만 gif
    if not '.gif' in ani_file and '.gif' in char_file:
        ani_image = same_scale_resize_height(GIF_HEIGHT, ani_image)

        char_frames = iter_frames(char_image)
        duration = char_image.info['duration']

        merged_images = []
        for char_frame in char_frames:
            char_frame = same_scale_resize_height(GIF_HEIGHT-50, char_frame)
            merged_image = image_merge_to_width_center(ani_image, char_frame,
                                                       GIF_MARGIN)
            merged_images.append(merged_image)

    # 동물 사진만 gif
    elif '.gif' in ani_file and not '.gif' in char_file:
        ani_frames = iter_frames(ani_image)
        duration = ani_image.info['duration']

        if duration < 80:
            duration = 80

        char_image = same_scale_resize_height(GIF_HEIGHT-50, char_image)

        merged_images = []
        for ani_frame in ani_frames:
            ani_frame = same_scale_resize_height(GIF_HEIGHT, ani_frame)
            merged_image = image_merge_to_width_center(ani_frame, char_image,
                                                       GIF_MARGIN)
            merged_images.append(merged_image)

    # 둘다 gif
    else:
        ani_duration = ani_image.info['duration']
        if ani_duration < 80:
            ani_duration = 80
        char_duration = char_image.info['duration']
        duration = round((ani_duration + char_duration)/2)

        ani_frames = iter_frames(ani_image)
        ani_frames = [x for x in ani_frames]

        char_frames = iter_frames(char_image)
        char_frames = [x for x in char_frames]

        ani_len, char_len = len(ani_frames), len(char_frames)

        if ani_len < char_len:
            ani_frames = ani_frames * math.ceil(char_len/ani_len)
            ani_frames = ani_frames[:char_len]
        elif ani_len > char_len:
            char_frames = char_frames * math.ceil(ani_len/char_len)
            char_frames = char_frames[:ani_len]

        frame_count = len(ani_frames)

        merged_images = []
        for i in range(frame_count):
            ani_frame = same_scale_resize_height(GIF_HEIGHT, ani_frames[i])
            char_frame = same_scale_resize_height(GIF_HEIGHT-50, char_frames[i])
            merged_image = image_merge_to_width_center(ani_frame, char_frame,
                                                       GIF_MARGIN)
            merged_images.append(merged_image)

    if not merged_images:
        continue

    merged_images[0].save(
        f'{MERGE_DIR}{file_name}.gif',
        save_all=True,
        append_images=merged_images[1:],
        duration=duration,loop=0
    )

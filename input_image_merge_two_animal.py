import os
import sys
import shutil
import glob
import math
import random
from PIL import Image

from functions import (
    get_min_len_and_random_list, create_file_name, iter_frames,
    same_scale_resize_height, image_merge_to_width_center,
    image_merge_to_height_center, same_scale_resize_width,
)

# 상수 설정
GIF_WIDTH = 300
GIF_HEIGHT = 325
GIF_MARGIN = 10

IMAGE_WIDTH = 900
IMAGE_HEIGHT = 900
IMAGE_MARGIN = 30

MAX_MERGE_LENGTH = 50

ANI_DIR = '../photo/reference/animal/'
CHAR_DIR = '../photo/reference/character/two_animal/'
MERGE_DIR = '../photo/merged/'


# 이미지 폴더 생성
if not os.path.exists(ANI_DIR):
    os.makedirs(ANI_DIR)

if not os.path.exists(CHAR_DIR):
    os.makedirs(CHAR_DIR)

if not os.path.exists(MERGE_DIR):
    os.makedirs(MERGE_DIR)


# input으로 정보 가져오기
ani_folder_names = input('동물폴더이름: ')
ani_ext = input('동물사진 확장자: ')
char_ext = input('캐릭터사진 확장자: ')

ani_ext = ani_ext if ani_ext else '*'
char_ext = char_ext if char_ext else '*'

# 동물사진 폴더별로 종류 지정 (미입력 시 모든 폴더의 파일 지정)
if not ani_folder_names:
    ani_folders = glob.glob(ANI_DIR + '*/')
    random.shuffle(ani_folders)
    ani_folder = ani_folders[0]
    ani_folder_sub = ani_folders[1]

    # 대상 이미지들 string 값으로 list 화/
    ani_files = []
    for ani_folder in ani_folders[len(ani_folders)//2:]:
        ani_files += glob.glob(ani_folder + f'*.{ani_ext}')

    ani_files_sub = []
    for ani_folder in ani_folders[:len(ani_folders)//2]:
        ani_files_sub += glob.glob(ani_folder + f'*.{ani_ext}')
else:
    ani_names = ani_folder_names.split(' ')
    if '' in ani_names or not len(ani_names) == 2:
        print('잘못된 입력')
        sys.exit()

    ani_folder = ANI_DIR + f'{ani_names[0]}/'
    ani_folder_sub = ANI_DIR + f'{ani_names[1]}/'

    # 대상 이미지들 string 값으로 list 화/
    ani_files = glob.glob(ani_folder + f'*.{ani_ext}')
    ani_files_sub = glob.glob(ani_folder_sub + f'*.{ani_ext}')

char_files = glob.glob(CHAR_DIR + f'*.{char_ext}')

# 반복횟수, 랜덤 리스트 get
min_len, ani_ran, char_ran = get_min_len_and_random_list(ani_files, char_files)
min_len_sub, ani_ran, ani_ran_sub = get_min_len_and_random_list(
    ani_files, ani_files_sub
)

min_len = min([min_len, min_len_sub])

# 최대 회수 지정
if min_len > MAX_MERGE_LENGTH:
    min_len = MAX_MERGE_LENGTH

# 이미지 합성
print(f'total count: {min_len}')
for i in range(min_len):
    print(i)

    # 파일 이름(string)
    ani_file = ani_files[ani_ran[i]]
    ani_file_sub = ani_files_sub[ani_ran_sub[i]]
    char_file = char_files[char_ran[i]]

    file_ = ani_file_sub
    ani_file_sub = char_file
    char_file = file_

    # pillow image
    ani_image = Image.open(ani_file)
    ani_image_sub = Image.open(ani_file_sub)
    char_image = Image.open(char_file)

    # 파일이름 랜덤 get
    file_name = create_file_name()

    if not '.gif' in ani_file and not '.gif' in char_file:
        ani_image = same_scale_resize_height(IMAGE_HEIGHT, ani_image)
        char_image = same_scale_resize_height(IMAGE_HEIGHT, char_image)
        merged_image = image_merge_to_width_center(ani_image, char_image,
                                                   IMAGE_MARGIN)

        # sub 동물사진 재합성
        if not '.gif' in ani_file_sub:
            ani_image_sub = same_scale_resize_width(
                merged_image.size[0], ani_image_sub
            )
            merged_image = image_merge_to_height_center(merged_image, ani_image_sub,
                                                       IMAGE_MARGIN)
            merged_image.save(f'{MERGE_DIR}{file_name}.png', 'png')
        else:
            ani_sub_frames = iter_frames(ani_image_sub)
            duration = ani_image_sub.info['duration']

            merged_image = same_scale_resize_height(GIF_HEIGHT, merged_image)
            merged_images = []
            for ani_sub_frame in ani_sub_frames:
                ani_sub_frame = same_scale_resize_width(
                    merged_image.size[0], ani_sub_frame
                )
                new_image = image_merge_to_height_center(
                    merged_image, ani_sub_frame, GIF_MARGIN
                )
                merged_images.append(new_image)

            merged_images[0].save(
                f'{MERGE_DIR}{file_name}.gif',
                save_all=True,
                append_images=merged_images[1:],
                duration=duration,loop=0
            )
        continue

    # 캐릭터사진만 gif
    if not '.gif' in ani_file and '.gif' in char_file:
        ani_image = same_scale_resize_height(GIF_HEIGHT, ani_image)

        char_frames = iter_frames(char_image)
        duration = char_image.info['duration']

        if duration < 80:
            duration = 80

        merged_images = []
        for char_frame in char_frames:
            char_frame = same_scale_resize_height(GIF_HEIGHT, char_frame)
            merged_image = image_merge_to_width_center(ani_image, char_frame,
                                                       GIF_MARGIN)
            merged_image = same_scale_resize_width(600, merged_image)
            merged_images.append(merged_image)

    # 동물 사진만 gif
    elif '.gif' in ani_file and not '.gif' in char_file:
        ani_frames = iter_frames(ani_image)
        duration = ani_image.info['duration']

        if duration < 80:
            duration = 80

        char_image = same_scale_resize_height(GIF_HEIGHT, char_image)

        merged_images = []
        for ani_frame in ani_frames:
            ani_frame = same_scale_resize_height(GIF_HEIGHT, ani_frame)
            merged_image = image_merge_to_width_center(ani_frame, char_image,
                                                       GIF_MARGIN)
            merged_image = same_scale_resize_width(600, merged_image)
            merged_images.append(merged_image)

    # 둘다 gif
    else:
        ani_duration = ani_image.info['duration']
        if ani_duration < 80:
            ani_duration = 80

        char_duration = char_image.info['duration']
        if char_duration < 80:
            char_duration = 80

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
            char_frame = same_scale_resize_height(GIF_HEIGHT, char_frames[i])
            merged_image = image_merge_to_width_center(ani_frame, char_frame,
                                                       GIF_MARGIN)
            merged_image = same_scale_resize_width(600, merged_image)
            merged_images.append(merged_image)

    if not merged_images:
        continue

    merged_image_width = merged_images[0].size[0]

    # sub 동물사진 재합성
    if not '.gif' in ani_file_sub:
        ani_image_sub = same_scale_resize_width(merged_image_width, ani_image_sub)

        pre_merged_images = merged_images
        merged_images = []
        for pre_merged_image in pre_merged_images:
            merged_image = image_merge_to_height_center(
                pre_merged_image, ani_image_sub, GIF_MARGIN
            )
            merged_images.append(merged_image)
    else:
        merged_duration = duration
        ani_sub_duration = ani_image_sub.info['duration']
        duration = round((merged_duration + ani_sub_duration)/2)

        merged_frames = merged_images

        ani_sub_frames = iter_frames(ani_image_sub)
        ani_sub_frames = [x for x in ani_sub_frames]

        merged_len, ani_sub_len = len(merged_frames), len(ani_sub_frames)

        if merged_len < ani_sub_len:
            merged_frames = merged_frames * math.ceil(ani_sub_len/merged_len)
            merged_frames = merged_frames[:ani_sub_len]
        elif merged_len > ani_sub_len:
            ani_sub_frames = ani_sub_frames * math.ceil(merged_len/ani_sub_len)
            ani_sub_frames = ani_sub_frames[:merged_len]

        frame_count = len(merged_frames)

        merged_images = []
        for i in range(frame_count):
            merged_frame = merged_frames[i]
            ani_sub_frame = same_scale_resize_width(merged_image_width, ani_sub_frames[i])
            merged_image = image_merge_to_height_center(merged_frame, ani_sub_frame,
                                                       GIF_MARGIN)
            merged_images.append(merged_image)

    merged_images[0].save(
        f'{MERGE_DIR}{file_name}.gif',
        save_all=True,
        append_images=merged_images[1:],
        duration=ani_sub_duration,loop=0
    )

import os
import sys
import glob
from PIL import Image

ANI_DIR = '../photo/reference/animal/'
ani_folders = glob.glob(ANI_DIR + '*/')
a = glob.glob(ANI_DIR + '*.*')


def get_all_dir_files(path, all_files=[]):
    files = glob.glob(path + '*.*')
    all_files += files

    child_folders = glob.glob(path + '*/')
    for child_folder in child_folders:
        get_all_files(child_folder, all_files)

    return all_files


all_files = get_all_files(ANI_DIR)

print(len(all_files))
for i in all_files:
    print(i)

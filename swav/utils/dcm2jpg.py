# dicom to jpeg conversion
import numpy as np
import os
import uuid
from PIL import Image
import pydicom as dicom
from dicom_reader import read_dicom_data
import random
import json
from tqdm import tqdm
from pathlib import Path
import matplotlib.pyplot as plt

def dicom2image(im_path, dest_im_type, dest_dir):

    slices = read_dicom_data(im_path)
    im_list = []
    for ii, im_slice in enumerate(slices):
        im_dict = dict()
        global im_id
        im_id_str = '{:08d}'.format(im_id)
        im_dict['id'] = im_id_str
        im_id += 1

        im_dict['source_im_path'] = im_path
        im_quant_uint8 = im_slice['rgb_image_uint8']
        im_quant_uint8 = Image.fromarray(im_quant_uint8)
        slice_unquant = im_slice['unquantized_frame_float32']

        unquant_im_name = '{}_slice_{}.npz'.format(im_id_str, ii)
        unquant_im_path = os.path.join(dest_dir, unquant_im_name)
        im_dict['unquant_im_path'] = unquant_im_path
        np.savez_compressed(unquant_im_path, slice_unquant)

        if dest_im_type.lower() in {'jpg', 'jpeg', '.jpg', '.jpeg'}:
            dest_im_name = '{}_slice_{}.JPG'.format(im_id_str, ii)
            dest_im_path = os.path.join(dest_dir, dest_im_name)
            im_dict['im_uint8_path'] = dest_im_path
            im_quant_uint8.save(dest_im_path)
            
        elif dest_im_type.lower() in {'png', '.png'}:
            dest_im_name = '{}_slice_{}.PNG'.format(im_id_str, ii)
            dest_im_path = os.path.join(dest_dir, dest_im_name)
            im_dict['im_uint8_path'] = dest_im_path
            im_quant_uint8.save(dest_im_path)
            
        im_list.append(im_dict)
    return im_list


def gen_uuid_dicom2image(root, files, file_types, dest_im_type, dest_dir):
    im_list = []
    print('processing dir: {}'.format(root))
    for file_name in tqdm(files):
        fn, ext = os.path.splitext(file_name)
        if ext in file_types:
            full_path = os.path.join(root, file_name)
            im_list_tmp = dicom2image(full_path, dest_im_type, dest_dir)
            im_list.extend(im_list_tmp)
    return im_list


def recursive_dicom2image(base_path, file_types, file_list, dest_im_type, dest_dir):
    im_list = []
    for root, dirs, files in os.walk(base_path):
        temp_im_list = gen_uuid_dicom2image(root, files, file_types, dest_im_type, dest_dir)
        im_list.extend(temp_im_list)
    return im_list
            
def verify_saved_data(dest_dir):
    npz_files = Path(dest_dir).glob('*.npz')
    for npz_file in npz_files:
        npz_data = np.load(npz_file)
        im_unq = npz_data['arr_0']
        plt.figure()
        plt.imshow(im_unq, cmap='gray')
        plt.axis('off')
        plt.pause(1)
        plt.close()


if __name__ == "__main__":

    im_id = 0
    base_dir = '/datastorage/ashim/TCIA/LUNG' # /Users/sudarshanr/Downloads/dicom_images
    dest_dir = '/datastorage/sudarshan/data/TCIA/LUNG' # /Users/sudarshanr/Downloads/dcm2jpg_images
    file_types = {".dcm", "dcm", 'nii', '.nii'}
    dest_im_type = 'JPG'
    file_list = dict()
    file_list = recursive_dicom2image(base_dir, file_types, file_list, dest_im_type, dest_dir)
    json_file = json.dumps(file_list)
    with open('lung_CT_dcm2jpg.json', 'w') as out_file:
        out_file.write(json_file)

    # Verification routine to verify images are loading correctly
    #verify_saved_data(dest_dir)
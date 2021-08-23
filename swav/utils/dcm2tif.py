# dicom to jpeg conversion
import numpy as np
import os
from PIL import Image
import pydicom as dicom

import random
import json
from tqdm import tqdm
from pathlib import Path
import matplotlib.pyplot as plt
import tifffile as tiff
import pydicom as py_dcm
from dicom_reader import read_dicom_data


def dicom2tiff(im_path, dest_im_type, dest_dir):
    global im_id
    im_id_str = '{:08d}'.format(im_id)
    temp_fn = '{}_slice_{}.tif'.format(im_id_str, 0)
    temp_dest_dir1 = os.path.join(dest_dir, 'MR', 'TIF', temp_fn)
    temp_dest_dir2 = os.path.join(dest_dir, 'CT', 'TIF', temp_fn)

    if os.path.isfile(temp_dest_dir1) or os.path.isfile(temp_dest_dir2):
        print('SKIPPING file: {}, already exists'.format(temp_fn))
        im_id += 1
    else:
        slices = read_dicom_data(im_path)
        im_list = []
        for ii, im_slice in enumerate(slices):

            if im_slice['modality'].lower() == 'mr':
                dest_dir = os.path.join(dest_dir, 'MR')
                dest_dir_set = True
            elif im_slice['modality'].lower() == 'ct':
                dest_dir = os.path.join(dest_dir, 'CT')
                dest_dir_set = True
            else:
                print('UNKNOWN IMAGING MODALITY, SKIPPING')
                dest_dir_set = False

            if dest_dir_set:

                im_dict = dict()
                im_id_str = '{:08d}'.format(im_id)
                im_dict['id'] = im_id_str
                im_id += 1

                im_dict['source_im_path'] = im_path
                slice_unquant = im_slice.pop('unquantized_frame_float32')

                tif_im_name = '{}_slice_{}.tif'.format(im_id_str, ii)
                dest_dir_tif = os.path.join(dest_dir, 'TIF')
                tif_im_path = os.path.join(dest_dir_tif, tif_im_name)
                tiff.imsave(tif_im_path, slice_unquant)
    return


def gen_uid_dicom2image(root, files, file_types, dest_im_type, dest_dir):
    print('processing dir: {}'.format(root))
    for file_name in tqdm(files):
        fn, ext = os.path.splitext(file_name)
        if ext in file_types:
            full_path = os.path.join(root, file_name)
            dicom2tiff(full_path, dest_im_type, dest_dir)
    return


def recursive_dicom2image(base_path, file_types, dest_im_type, dest_dir):
    for root, dirs, files in os.walk(base_path):
        gen_uid_dicom2image(root, files, file_types, dest_im_type, dest_dir)
    return


def verify_saved_data(metadata_dir):
    meta_files = Path(metadata_dir).glob('*.json')
    for meta_file in meta_files:
        with open(meta_file, 'r') as js_file:
            json_data = json.load(js_file)
        js_file.close()
        source_path = json_data['source_im_path']

        slices = read_dicom_data(source_path)
        dicom_px_array = slices[0]['unquantized_frame_float32']
        temp_fn = os.path.splitext(os.path.split(json_data['unquant_im_path'])[1])[0] + '.tif'
        tif_path = os.path.join(os.path.split(os.path.split(json_data['unquant_im_path'])[0])[0], 'TIF', temp_fn)
        tif_img = tiff.imread(tif_path)
        abs_diff = np.sum(np.abs(tif_img-dicom_px_array))
        print('abs. diff betn dicom and tiff image is : {}'.format(abs_diff))

    return


if __name__ == "__main__":
# For Brain the code is run on dev2 machine
    im_id = 0
    base_dir = '/Users/sudarshanr/Downloads/dicom_images/dicom_images0' # /datastorage/sudarshan/TCIA/BRAIN/
    dest_dir = '/Users/sudarshanr/Downloads/dcm2jpg_images/BRAIN/' #  #/datastorage/sudarshan/data/TCIA/BRAIN
    file_types = {".dcm", "dcm", 'nii', '.nii'}
    dest_im_type = 'TIF'
    recursive_dicom2image(base_dir, file_types, dest_im_type, dest_dir)
    #metadata_dir = '/Users/sudarshanr/Downloads/dcm2jpg_images/BRAIN/MR/METADATA/'
    #verify_saved_data(metadata_dir)

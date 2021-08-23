from pydicom.pixel_data_handlers.numpy_handler import get_pixeldata
from pydicom.pixel_data_handlers.util import apply_color_lut, convert_color_space
import pydicom as dicom
import numpy as np

import os
import warnings
import copy

def get_image(ds, frame_num=0, num_frames=1):

    if 'Columns' in ds.dir():
        width = ds.Columns
    else:
        width = None
    if 'Rows' in ds.dir():
        height = ds.Rows
    else:
        height = None
    # print('Image Size (width, height) =', width, height)
    spp = ds.SamplesPerPixel
    phi = ds.PhotometricInterpretation
    bs = ds.BitsStored if 'BitsStored' in ds.dir() else None
    bpp = ds.BitsAllocated
    pr = ds.PixelRepresentation
    pc = 0 
    if "PlanarConfiguration" in ds.dir():
        pc = ds.PlanarConfiguration

    if num_frames > 1:
        image = ds.pixel_array[frame_num]
    else:
        image = ds.pixel_array

    if len(image.shape) == 1:
        image = image.reshape(height, width)

    tmp = None
    if phi == 'PALETTE COLOR':
        tmp = apply_color_lut(image, ds)
    elif phi == 'YBR_FULL' or phi == 'YBR_FULL_422':
        tmp = convert_color_space(image, phi, 'RGB')
        pc = 0
        # print("Force pc = 0 after color_conversion")
    else:
        tmp = image

    if pc == 1 and spp > 1:
        tmp1 = np.empty(spp, height, width)
        for i in range(spp):
            tmp1[i] = tmp[i::spp]
        tmp = tmp1

    if pr == 1:
        if bs is not None:
            mid_val = pow(2, (bs-1))
        elif bpp is not None:
            mid_val = pow(2, (bpp-1))
        else:
            mid_val = 0
            warnings.warn('No Bit Depth info present. Unable to convert image from Signed to Unsigned representation.')
        tmp = tmp.astype(np.int32)
        tmp = tmp + mid_val

    img_unquantized = copy.deepcopy(tmp) 
    if bpp != 8 or tmp.dtype != np.uint8:
        img_min = np.amin(tmp)
        img_max = np.amax(tmp)
        img_range = max(img_max - img_min, 1).astype('float32')
        tmp = ((tmp - img_min)/img_range)
        rgb = (tmp*255).astype('uint8')
    else:
        rgb = tmp.astype('uint8')

    if len(rgb.shape) == 1:
        rgb = np.array(rgb)
        rgb = rgb.reshape((height, width))
    
    if spp == 1:
       tmp = rgb
       rgb = np.asarray(np.dstack((tmp, tmp, tmp)), dtype=np.uint8)

    return np.array(rgb).astype(np.uint8), img_unquantized.astype('float32') 


def read_dicom_data(image_path):

    try:
        frames = []
        ds = dicom.dcmread(image_path)

        if 'NumberOfFrames' in ds.dir():
            num_frames = ds.NumberOfFrames
        else:
            num_frames = 1

        if num_frames > 1:
            for frame_num in range(num_frames):
                im_rgb, im_unquant = get_image_frame(ds, frame_num, num_frames)
                frame_dict = dict()
                frame_dict['frame_num'] = frame_num
                frame_dict['rgb_image_uint8'] = im_rgb
                frame_dict['unquantized_frame_float32'] = im_unquant
                frames.append(frame_dict)

        else:
            frame_num = 0
            im_rgb, im_unquant = get_image(ds, frame_num, num_frames)
            frame_dict = dict()
            frame_dict['frame_num'] = frame_num
            frame_dict['rgb_image_uint8'] = im_rgb
            frame_dict['unquantized_frame_float32'] = im_unquant
            frames.append(frame_dict)
        return frames

    except Exception as e:
        print(e)
        print('Failed with exception for image: ' + image_path)
        return []

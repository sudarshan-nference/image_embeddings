# function to compute running mean and standard deviation of streaming data
import numpy as np
import os
import tifffile as tiff


def sum_sumsq_1ch(root, files):
    ch_sums = 0.0
    ch_sumsq = 0.0

    ch_sums_resc = 0.0
    ch_sumsq_resc = 0.0

    global num_images
    
    for ii,im_file in enumerate(files):
        im_path = os.path.join(root, im_file)
        if im_path[-3:] == 'tif':
            im = np.array(tiff.imread(im_path))

            
            ch_sums += np.mean(im)
            ch_sumsq += np.std(im)

            # rescale the image to [0,1] range
            im_resc = (im - np.min(im))/(np.max(im) - np.min(im))
            if not np.isnan(np.mean(im_resc)) and not np.isnan(np.std(im_resc)):
                ch_sums_resc += np.mean(im_resc)
                ch_sumsq_resc += np.std(im_resc)
                num_images += 1
            #print('img mean: {} std: {} mean_rescaled: {} std_rescaled: {}'.format(np.mean(im), np.std(im), np.mean(im_resc), np.std(im_resc)))
            if num_images % 10000 == 0:
                print('processed {} images, rescaled sum: {}, rescaled sum squared: {}'.format(num_images, ch_sums_resc, ch_sumsq_resc)) 


    return ch_sums, ch_sumsq, ch_sums_resc, ch_sumsq_resc


def stream_mean_std_recursive_1ch(im_folder):
    global num_images
    
    mean_sum = 0.0
    std_sum = 0.0
    mean_resc_sum = 0.0
    std_resc_sum = 0.0
    for root, dirs, files in os.walk(im_folder):
        x, xsq, x_resc, xsq_resc = sum_sumsq_1ch(root, files)
        mean_sum += x
        std_sum += xsq
        mean_resc_sum += x_resc
        std_resc_sum += xsq_resc
    means = mean_sum/float(num_images)
    #vars = xsq_sum/float(num_images) - np.multiply(means, means)
    #stds = np.sqrt(vars)
    stds = std_sum/float(num_images)

    means_resc = mean_resc_sum/float(num_images)
    #vars_resc = xsq_resc_sum/float(num_images) - np.multiply(means_resc, means_resc)
    #stds_resc = np.sqrt(vars_resc)
    stds_resc = std_resc_sum/float(num_images)
    return means, stds, means_resc, stds_resc
    

if __name__ == "__main__":
    num_images = 0.0
    im_folder = '/dev2-datastorage/sudarshan/data/TCIA/BRAIN_TEMP/MR/TIF'
    #'/Users/sudarshanr/Downloads/dcm2jpg_images/BRAIN/MR/TIF'
    means, stds, means_resc, stds_resc = stream_mean_std_recursive_1ch(im_folder)
    print('Num images used: {}'.format(num_images))
    print('means')
    print(means)
    print('stds')
    print(stds)

    print('means rescaled[0,1]')
    print(means_resc)
    print('stds rescaled [0,1]')
    print(stds_resc)

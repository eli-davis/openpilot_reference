# B"H

import struct
import numpy as np

def load_image_from_file(filename):
    with open(filename, 'rb') as f:
        width = struct.unpack('Q', f.read(8))[0]
        height = struct.unpack('Q', f.read(8))[0]
        stride = struct.unpack('Q', f.read(8))[0]
        uv_offset = struct.unpack('Q', f.read(8))[0]
        #print(width, height, stride, uv_offset)
        y_plane = np.fromfile(f, dtype=np.uint8, count=height*stride).reshape(height, stride)
        uv_plane = np.fromfile(f, dtype=np.uint8, count=height//2*stride).reshape(height//2, stride)

    return y_plane, uv_plane

def load_images():

    folder_path ="/home/deepview/openpilot/selfdrive/modeld/data"

    for img_i in range(1, 100):

        main_img_path = f"{folder_path}/{img_i}_main_cam.bin"
        wide_img_path = f"{folder_path}/{img_i}_main_cam.bin"

        y_main, uv_main   = load_image_from_file(main_img_path)
        y_extra, uv_extra = load_image_from_file(wide_img_path)

        print(f"main_cam y.shape={y_main.shape} uv.shape={uv_main.shape}")
        print(f"wide_cam y.shape={y_extra.shape} uv.shape={uv_extra.shape}")

if __name__ == "__main__":
    load_images()

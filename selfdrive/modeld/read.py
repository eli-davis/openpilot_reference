import struct
import numpy as np

def load_image_from_file(filename):
    with open(filename, 'rb') as f:
        width = struct.unpack('Q', f.read(8))[0]
        height = struct.unpack('Q', f.read(8))[0]
        stride = struct.unpack('Q', f.read(8))[0]
        uv_offset = struct.unpack('Q', f.read(8))[0]
        print(width, height, stride, uv_offset)
        y_plane = np.fromfile(f, dtype=np.uint8, count=height*stride).reshape(height, stride)
        uv_plane = np.fromfile(f, dtype=np.uint8, count=height//2*stride).reshape(height//2, stride)

    return y_plane, uv_plane

y_main, uv_main = load_image_from_file('main_image.bin')
y_extra, uv_extra = load_image_from_file('extra_image.bin')

print(y_main.shape, uv_main.shape)
print(y_extra.shape, uv_extra.shape)
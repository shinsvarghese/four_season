mipi_format = 'MiPi'
imta_format = 'iMTA'

mfc510_width_in = 1176
mfc510_height_in = 640

mfc510_pyramid_levels_y = {
    'y2': {'width': 1152, 'height': 640},
    'y3': {'width': 576, 'height': 320},
    'y4': {'width': 288, 'height': 160},
    'y5': {'width': 144, 'height': 80},
    'y6': {'width': 72, 'height': 40}
}

mfc510_pyramid_levels_uv = {
    'uv3': {'width': 576, 'height': 320},
    'uv4': {'width': 288, 'height': 160},
    'uv5': {'width': 144, 'height': 80},
    'uv6': {'width': 72, 'height': 40}
}

mfc510_raw_meta = {
    "pattern": "rggb",
    "size_x": mfc510_width_in,
    "size_y": mfc510_height_in,
    "format": mipi_format
}


def get_image_format(image):
    """ Decide it is a png or bin image
    bin: 0, png: 1

    :param image: bytes array, image content
    :return: int, 0 or 1
    """
    image_size = len(image)
    if image_size == 1136016:
        return 0

    return 1

from math import sqrt
from PIL import Image


def get_color_distance(color1, color2):
    return sqrt(
        (color1[0] - color2[0]) ** 2
        + (color1[1] - color2[1]) ** 2
        + (color1[2] - color2[2]) ** 2
    )


def getAllPixelsFromImage(image_path):
    image = Image.open(image_path)
    rgb_pixel_values = list(image.getdata())
    for pixel in rgb_pixel_values:
        findClosestColorInDict(pixel)

    return rgb_pixel_values


def findClosestColorInDict(rgb_value):
    dict = imagesToRGBDict()
    closest = 500
    for key, value in dict:
        if get_color_distance(rgb_value, key) < closest:
            closest = value

    return closest


def imagesToRGBDict(imagesPath):
    pass """ aca generamos un dict con RGBVAlue, pathDeLaImagen """
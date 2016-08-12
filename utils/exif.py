import pyexiv2


def get_metadata(path):
    return pyexiv2.ImageMetadata(path)

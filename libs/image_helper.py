import os
import re
from typing import Union

from werkzeug.datastructures import FileStorage
from flask_uploads import IMAGES, UploadSet

IMAGE_SET = UploadSet("images", IMAGES)


def save_image(image: FileStorage, folder: str = None, name: str = None) -> str:
    """Takes a FileStorage and saves it to a folder"""
    return IMAGE_SET.save(image, folder, name)


def get_path(filename: str = None, folder: str = None) -> str:
    """Take image name and folder and return full path"""
    return IMAGE_SET.path(filename, folder)


def find_image_any_format(filename: str, folder: str) -> Union[str, None]:
    """Take a filename and return an image on any of the accepted formats"""
    for _format in IMAGES:
        image = f"{filename}.{_format}"
        image_path = IMAGE_SET.path(filename=image, folder=folder)
        if os.path.isfile(image_path):
            return image
    
    return None


def _retrieve_filename(file: Union[str, FileStorage]) -> str:
    """Take FileStorage and return file name"""
    if isinstance(file, FileStorage):
        return file.filename
    return file


def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    """Check our regex and return whether the string mathces or not"""
    filename = _retrieve_filename(file)
    allowed_format = "|".join(IMAGES)
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$" # (png|jpg|jpeg)
    return re.match(regex, filename)


def get_basename(file: Union[str, FileStorage]) -> str:
    """Return full name of image in the path"""
    filename = _retrieve_filename(file)
    return os.path.split(filename)[1]


def get_extension(file: Union[str, FileStorage]) -> str:
    """Return file extension of the image"""
    filename = _retrieve_filename(file)
    return os.path.splitext(filename)[1]

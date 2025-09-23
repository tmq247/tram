import os

from ..logging import LOGGER
import logging
from os import listdir, mkdir

# remove all files on startup  that contains these extentions
files = [
    ".jpg",
    ".jpeg",
    ".mp3",
    ".m4a",
    ".mp4",
    ".webm",
    ".png",
]


def dirr():
    downloads_folder = "downloads"
    cache_folder = "cache"

    for file in os.listdir():
        if any(file.endswith(ext) for ext in files):
            os.remove(file)

    if downloads_folder not in listdir():
        mkdir(downloads_folder)

    if cache_folder not in listdir():
        mkdir(cache_folder)

    LOGGER(__name__).info("Danh mục được cập nhật.")


    #logging.info("Directories Updated.")


#def dirr():
    #for file in os.listdir():
        #if file.endswith(".jpg"):
            #os.remove(file)
        #elif file.endswith(".jpeg"):
            #os.remove(file)
        #elif file.endswith(".png"):
            #os.remove(file)

    #if "downloads" not in os.listdir():
        #os.mkdir("downloads")
    #if "cache" not in os.listdir():
       # os.mkdir("cache")

    #LOGGER(__name__).info("Danh mục được cập nhật.")

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

BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

def dirr():
    for file in os.listdir():
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            os.remove(file)

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    LOGGER(__name__).info("Directories Updated.")

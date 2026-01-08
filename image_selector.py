"""
image_selector.py
Functions for selecting images based on mood
"""
import os
import random
from utils import list_files_in_folder

VALID_IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

def get_images_from_folder(folder: str) -> list[str]:
    """
    Get all images (png/jpg) from a folder.
    """
    return [
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if file.lower().endswith(VALID_IMG_EXT)
    ]

def select_image(mood: str) -> str:
    """
    Randomly select one image path from a folder based on mood.
    Folders: 'images/positive', 'images/negative', 'images/neutral'
    Returns:
        str: Path of selected image
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mood_folders = {
        'positive': os.path.join(base_dir, 'images/positive'),
        'negative': os.path.join(base_dir, 'images/negative'),
        'neutral': os.path.join(base_dir, 'images/neutral')
    }

    folder = mood_folders.get(mood.lower(), mood_folders['neutral'])

    images = get_images_from_folder(folder)
    if not images:
        raise FileNotFoundError(f"No images found in folder: {folder}")

    return random.choice(images)
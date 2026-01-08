"""
image_selector.py
Functions for selecting images based on mood
"""
import os
import random
from utils import list_files_in_folder

def get_images_from_folder(folder: str) -> list[str]:
    """
    Get all images (png/jpg) from a folder.
    """
    return [
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if file.lower().endswith(('.png', '.jpg'))
    ]

def select_image(mood: str) -> str:
    """
    Randomly select one image from a folder based on mood.
    Folders: 'images/positive', 'images/negative', 'images/neutral'
    Returns:
        str: Path of selected image
    """
    mood_folders = {
        'positive': 'images/positive',
        'negative': 'images/negative',
        'neutral': 'images/neutral'
    }

    folder = mood_folders.get(mood.lower())
    if not folder or not os.path.exists(folder):
        raise ValueError(f"Invalid mood or folder does not exist: {mood}")

    images = get_images_from_folder(folder)
    if not images:
        raise FileNotFoundError(f"No images found in folder: {folder}")

    return random.choice(images)
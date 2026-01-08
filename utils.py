import os
from typing import List, Any
import random

def list_files_in_folder(folder: str, extensions: list = ["png", "jpg"]) -> List[str]:
    """
    Return a list of files in folder with the given extensions
    """
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(tuple(extensions))
    ]

def random_choice_from_list(lst: list) -> Any:
    """
    Return a random element from a list
    """
    return random.choice(lst)

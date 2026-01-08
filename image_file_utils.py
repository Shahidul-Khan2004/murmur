from PIL import Image, ImageFile
from datetime import datetime
import os
import io

def save_image_current_time(img_data: ImageFile.ImageFile | bytes, folder: str, ext=".png") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(folder, timestamp) + ext
    if type(img_data) is ImageFile.ImageFile:
        img_data.save(path)
    elif type(img_data) is bytes:
        image_file = io.BytesIO(img_data)
        img = Image.open(image_file)
        img.save(path)
    return path
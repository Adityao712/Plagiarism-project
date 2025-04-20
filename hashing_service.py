from PIL import Image
import imagehash

def get_image_hash(image_path):
    image = Image.open(image_path)
    return imagehash.phash(image)

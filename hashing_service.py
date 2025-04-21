from PIL import Image
import imagehash

def get_image_hash(file_path):
    try:
        img = Image.open(file_path)
        hash_val = imagehash.average_hash(img)
        return str(hash_val)
    except Exception as e:
        print("Hashing Error:", e)
        raise

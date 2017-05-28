import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
from squadrun_task import settings




def store_to_cloudinary(image_path):
    """
    Function to store the compressed image to CLoudinary Onine Storage
    :param image_path: 
    :return: 
    """
    try:
        cloudinary.config(
            cloud_name=settings.CLOUD_NAME,
            api_key=settings.API_KEY,
            api_secret=settings.API_SECRET
        )
        cloudinary_response = cloudinary.uploader.upload(image_path)
        response = {'error': '', 'status': True, 'cloudinary_response':cloudinary_response}
    except Exception as e:
        response = {'error': repr(e), 'status': False, 'cloudinary_response': ''}
    return response


def compress_image(image_path,image_name):
    """
    Function to compress the image to 50% of its quality 
    :param image_path: 
    :param image_name: 
    :return: 
    """
    try:
        image = Image.open(image_path + image_name)
        image.save(image_path + 'compressed_' + image_name, quality=50, optimised=True)
        response = {'error':'', 'status': True, 'compressed_image_path':image_path + 'compressed_' + image_name}
    except Exception as e:
        response = {'error': repr(e), 'status': False, 'compressed_image_path': ''}

    return response
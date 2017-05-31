import xlwt
import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
from squadrun_task import settings
import logging

logger = logging.getLogger("default")
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
        response = {'error': '', 'status': True, 'cloudinary_response': cloudinary_response}
    except IOError:
        logger.error('Path error while uploading to cloudinary '+image_path)
        response = {'error':'Error while uploading file to cloud','status': False, 'cloudinary_response': ''}
    return response


def compress_image(image_path,image_name, quality):
    """
    Function to compress the image to 50% of its quality 
    :param image_path: 
    :param image_name: 
    :return: 
    """
    try:
        if not quality:
            quality = 50
        compress_params = {"quality": quality, "optimised": True}
        if image_name.split('.')[1] == 'gif':
            compress_params = {"quality": quality, "optimised": True, 'save_all': True}
        image = Image.open(image_path + image_name)
        image.save(image_path + 'compressed_'+str(quality) + image_name,**compress_params)
        response = {'error':'', 'status': True, 'compressed_image_path': image_path + 'compressed_'+str(quality) +image_name}
    except IOError:
        logger.error('Path error while compressing the file'+ image_path)
        response = {'error': 'Problem in saving the file', 'status': False, 'compressed_image_path': ''}

    return response


def map_to_original(image_list_original,image_list_compressed):
    try:
        wb = xlwt.Workbook()
        ws = wb.add_sheet("Mapping Sheet")
        ws.write(0,0,'Original Image Url')
        ws.write(0,1,'Compressed Image  Url')
        ws.write(0,2,'Extraction type')
        for i in range(0,len(image_list_original)):
            ws.write(i+1,0,image_list_original[i].get('url'))
            ws.write(i + 1, 1, image_list_compressed[i])
            ws.write(i + 1, 2, image_list_original[i].get('message'))
        ws.col(0).width = 256 * max([len(image.get('url')) for image in image_list_original])
        ws.col(1).width = 256 * max([len(image) for image in image_list_compressed])
        ws.col(2).width = 256 * max([len(image.get('message')) for image in image_list_original])
        wb.save('mapping.xls')
        response = {'error': '', 'status':True}
    except Exception as e:
        response = {'error': repr(e), 'status': False}
    return response

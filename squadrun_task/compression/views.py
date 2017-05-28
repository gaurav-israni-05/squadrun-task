
from django.shortcuts import render
from rest_framework.views import View,APIView
import urllib.request
from squadrun_task.settings import *
from PIL import Image
from compression import serializers as compression_serializers
from compression import utils as compression_utils

# Create your views here.

class Index(View):
    template_name = 'upload_form.html'


    def get(self,request):
        """
        Renders the template 'upload_form.html'
        :param request: 
        :return: 
        """
        return render(request,self.template_name)

    def post(self,request):
        """
        Retrieve the images from url's provided in file,then compress them and store their location in a file 
        :param request: 
        :return: 
        """
        data = {}
        data['txt_file'] = request.FILES.get('txt_file')
        data['xls_file'] = request.FILES.get('xls_file')
        data['physical_image'] = request.FILES.get('physical_image')
        data['single_image_url'] = request.POST.get('single_image_url')
        image_list_serializer = compression_serializers.ImageListGetSerializer(data=data)
        if not image_list_serializer.is_valid():
            response = {'error':'Error in data provided','extracted':False}
        else:
            extracted = True
            validated_data = image_list_serializer.validated_data
            image_list_original = []
            image_list_compressed = []
            error = ""
            image_url_list = validated_data.get('image_list')
            f = open('compressed_urls', 'a')
            #Case when Physical Image Data is provided
            if validated_data.get('physical_image'):
                image_path = BASE_DIR + '/static/'
                image_name = validated_data['physical_image']
                image_list_original.append(image_name)
                compress_response = compression_utils.compress_image(image_path=image_path,image_name=image_name)
                if compress_response.get('status'):
                    cloudinary_response = compression_utils.store_to_cloudinary(compress_response.get('compressed_image_path'))
                    if cloudinary_response.get('status'):
                        f.write(cloudinary_response['cloudinary_response'].get('url')+'\n')
                        image_list_compressed.append(cloudinary_response['cloudinary_response'].get('url'))
            # Parsing the image list returned from serializer
            for url in validated_data['image_list']:
                image_name = url.rsplit('/', 1)[1]
                image_path = BASE_DIR+STATIC_URL
                #Handle the case where file is not present at the URL or there is problem while compressing
                try:
                    urllib.request.urlretrieve(url, image_path+image_name)
                    image_list_original.append(image_name)
                    compress_response = compression_utils.compress_image(image_path=image_path, image_name=image_name)
                    if compress_response.get('status'):
                        cloudinary_response = compression_utils.store_to_cloudinary(compress_response.get('compressed_image_path'))
                        if cloudinary_response.get('status'):
                            f.write(cloudinary_response['cloudinary_response'].get('url') + '\n')
                            image_list_compressed.append(cloudinary_response['cloudinary_response'].get('url'))
                except:
                    error += "Error while processing "+url
            f.close()
            response = {'extracted_images': image_list_original, 'compressed_images': image_list_compressed,
                        'extracted': extracted, 'error': error}
        return render(request, self.template_name, context=response)
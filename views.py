from django.shortcuts import render
from rest_framework.views import View,APIView
import urllib.request
from squadrun_task.settings import *
from PIL import Image
from compression import serializers as compression_serializers
from compression import utils as compression_utils
from compression import constants as compression_constants

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
        data['single_image_quality'] = request.POST['single_image_quality'] if request.POST.get('single_image_quality') !=  '' else None
        data['txt_file_quality'] = request.POST['txt_file_quality'] if request.POST.get('txt_file_quality') !=  '' else None
        data['xls_file_quality'] = request.POST['xls_file_quality'] if request.POST.get('xls_file_quality') !=  '' else None
        data['physical_image_quality'] = request.POST['physical_image_quality'] if request.POST.get('physical_image_quality') !=  '' else None
        image_list_serializer = compression_serializers.ImageListGetSerializer(data=data)
        if not image_list_serializer.is_valid():
            response = {'error': 'There is some problem in the input data', 'extracted':False}
        else:
            extracted = True
            validated_data = image_list_serializer.validated_data
            image_url_list = validated_data.get('image_list')
            image_list_original = []
            image_list_compressed = []
            image_list_original_written = []
            error = ""
            # Parsing the image list returned from serializer
            for image_data in image_url_list:
                url = image_data['url']
                if image_data['type'] == compression_constants.UPLOADED_TYPE['physical']:
                    image_name = url
                else:
                    image_name = url.rsplit('/', 1)[1]
                image_path = BASE_DIR+STATIC_URL
                #Handle the case where file is not present at the URL or there is problem while compressing
                try:
                    if not image_data['type'] == compression_constants.UPLOADED_TYPE['physical']:
                        urllib.request.urlretrieve(url, image_path+image_name)
                    image_list_original.append(image_name)
                    compress_response = compression_utils.compress_image(image_path=image_path, image_name=image_name,
                                                                         quality=image_data['quality'])
                    if compress_response.get('status'):
                        cloudinary_response = compression_utils.store_to_cloudinary(compress_response.get('compressed_image_path'))
                        if cloudinary_response.get('status'):
                            image_list_original_written.append({'url':image_data['url'],'message':
                                                                compression_constants.UPLOADED_TYPE_MESSAGE[image_data['type']]})
                            image_list_compressed.append(cloudinary_response['cloudinary_response'].get('url'))
                        else:
                            error += cloudinary_response.get('error')+'\n'
                    else:
                        error += compress_response.get('error')
                except urllib.request.URLError:
                    error += 'There was no image found at'+url +'\n'
            compression_utils.map_to_original(image_list_original_written,image_list_compressed)
            response = {'extracted_images': image_list_original, 'compressed_images': image_list_compressed,
                        'extracted': extracted, 'error': error}
        return render(request, self.template_name, context=response)
import xlrd
from rest_framework import serializers
from django.core.files.storage import FileSystemStorage
from squadrun_task.settings import BASE_DIR
from compression import constants as compression_constants

class ImageListGetSerializer(serializers.Serializer):
    """
    Serializer to verify the data provided and create a list of image urls 
    """
    txt_file = serializers.FileField(required=False,allow_null=True)
    xls_file = serializers.FileField(required=False,allow_null=True)
    physical_image = serializers.ImageField(required=False,allow_null=True)
    single_image_url = serializers.CharField(required=False,allow_blank=True)
    single_image_quality = serializers.IntegerField(min_value=1,max_value=100,required=False,allow_null=True)
    txt_file_quality = serializers.IntegerField(min_value=1, max_value=100,required=False,allow_null=True)
    xls_file_quality = serializers.IntegerField(min_value=1, max_value=100,required=False,allow_null=True)
    physical_image_quality = serializers.IntegerField(min_value=1, max_value=100,required=False,allow_null=True)
    image_list = serializers.ListField(required=False)


    def validate(self, data):
        if not(data.get('txt_file') or data.get('xls_file') or data.get('physical_image') or data.get('single_image_url')):
            raise serializers.ValidationError('No file or url provided')
        image_url_list = []
        if data.get('single_image_url'):
            image_url_list.append({'url': data['single_image_url'], 'quality':  data['single_image_quality'],'type':
                                   compression_constants.UPLOADED_TYPE['single']})
        if data.get('txt_file'):
            file = data['txt_file']
            if file.name.split('.')[1] != 'txt':
                raise serializers.ValidationError('Text File must be provided')
            fs = FileSystemStorage(location=BASE_DIR + '/url_files/')
            filename = fs.save(file.name, file)
            input_file = open(BASE_DIR + '/url_files/' + filename, 'r')
            for url in input_file.read().splitlines():
                image_url_list.append({'url': url, 'quality': data['txt_file_quality'],'type':
                                        compression_constants.UPLOADED_TYPE['txt_file']})
        if data.get('xls_file'):
            file = data['xls_file']
            if file.name.split('.')[1] != 'xls':
                raise serializers.ValidationError('XLS File must be provided')
            fs = FileSystemStorage(location=BASE_DIR + '/url_files/')
            filename = fs.save(file.name,file)
            input_file = xlrd.open_workbook(BASE_DIR + '/url_files/' + filename)
            for i in range(0,input_file.nsheets):
                sheet = input_file.sheet_by_index(i)
                for row in range(0,sheet.nrows):
                    for value in sheet.row_values(row):
                        image_url_list.append({'url': value, 'quality': data['xls_file_quality'],'type':
                                                compression_constants.UPLOADED_TYPE['xls_file']})
        if data.get('physical_image'):
            image = data['physical_image']
            fs = FileSystemStorage(location=BASE_DIR + '/static/')
            filename = fs.save(image.name, image)
            data['physical_image'] = filename
            image_url_list.append({'url': filename, 'quality': data['physical_image_quality'], 'type':
                                   compression_constants.UPLOADED_TYPE['physical']})
        data['image_list'] = image_url_list
        return data




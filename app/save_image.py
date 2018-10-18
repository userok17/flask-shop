from uuid import uuid4
import os
import re
from PIL import Image
from io import BytesIO

class InvalidExtension(Exception):
    pass
        

class ResizeImage:
    ''' Изменить изображение'''
    def __init__(self, image):
        self.__image = image
        self.__width = self.__image.size[0]
        self.__height = self.__image.size[1]
    
    def resize_by_width(self, width):
        '''Подогнать высоту и вернуть новый размер текущего изображения'''
        if not isinstance(width, int):
            raise TypeError('Значение width должен быть типа int')
        width_percent = width / self.__width
        height = round(self.__height * width_percent)
        return self.__image.resize((width, height), Image.LANCZOS)
    
    def resize_by_height(self, height):
        '''Подогнать высоту и вернуть новый размер текущего изображения'''
        if not isinstance(height, int):
            raise TypeError('Значение height должен быть типа int')
        height_percent = height / self.__height
        width = round(self.__width * height_percent)
        return self.__image.resize((width, height), Image.LANCZOS)
    
    def resize(self, width=None, height=None):
        ''' Изменить размер изображение'''
        width = width or self.__width
        height = height or self.__height
        return self.__image.resize((width, height), Image.LANCZOS)
    

class SaveImage:
    '''Сохранить изображение'''
    def __init__(self, data, upload_path, filename=None):
        self.__image = Image.open(data)
        self.__upload_path = upload_path
        self.__filename = self.__get_filename(filename)
    
    @property
    def filename(self):
        '''Получить имя файла'''
        return self.__filename
    
    @filename.setter
    def filename(self, value):
        '''Установить пользотельское название файла'''
        self.__filename = value
    
    def __get_filename(self, filename):
        '''Получить имя файла для сохранения'''
        if not filename:
            filename = '{}.jpg'.format(str(uuid4()))
            if os.path.exists(os.path.join(self.__upload_path, filename)):
                filename = self.__get_filename()
        return filename
        
 
    def resize(self, width=None, height=None, auto_resize=False):
        '''Изменить размер изображение'''
        resize_image = ResizeImage(self.__image)
        if auto_resize == True:
            '''Авторазмер изображение'''
            if width is None and height is not None:
                '''Подогнать изображение по высоте'''
                self.__image = resize_image.resize_by_height(height)
            elif width is not None and height is None:
                '''Подогнать изображение по ширине'''
                self.__image = resize_image.resize_by_width(width)
            else:
                self.__image = resize_image.resize(width, height)
        else:
            '''Без авто размера'''
            self.__image = resize_image.resize(width, height)
    
    def save(self):
        '''Сохранить изображение'''
        self.__image.save(os.path.join(self.__upload_path, self.__filename))
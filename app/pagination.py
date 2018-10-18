#!/usr/bin/env python3
from flask import request
class Paginator:
    def __init__(self, count_messages = 10, total_posts = 0, page = 1):
        '''
        :param count_message: Переменная хранит число сообщений выводимых на станице  
        :param total_posts: Общее число сообщений в базе данных
        :param page: начало сообщений для текущей страницы 
        :return void
        '''
        self.__count_messages = count_messages
        self.__total_posts = total_posts
        self.__page = page
    
    @property
    def __count_pages(self):
        '''
        Полное Количество страниц
        :return int
        '''
        return (self.__total_posts - 1) // self.__count_messages + 1
    
    
    def get_page_links(self, url):
        '''
        Получить ссылки постраничной навигации
        :param адрес страницы
        :return str
        '''
        
        first_page = ''
        next_page = ''
        page2_left = ''
        page1_left = ''
        page2_right = ''
        page1_right = ''
        # Проверяем, если страница только одна то отправляем возвращаем пустую строку
        if self.__count_pages == 0 or self.__count_pages == 1:
            return ''
        
        params = ''
        if request.args:
            params = '?'
            args_list = []
            for key, value in request.args.items():
                args_list.append('{}={}'.format(key, value))
            params += '&'.join(args_list)
        
        # Проверяем нужны ли стрелки назад
        if self.__page != 1:
            first_page = '<a href="{0}{1}/{2}">Предыдущая</a>'.format(url, self.__page -1, params)
        
        # Проверяем нужны ли стрелки вперед
        if self.__page != self.__count_pages:
            next_page = '<a href="{0}{1}/{2}">Следующая</a>'.format(url, self.__page + 1, params)
        
        # Находим две ближайшие станицы с обоих краев, если они есть
        if self.__page - 2 > 0:
            page2_left = '<a href="{0}{1}/{2}">{1}</a>'.format(url, self.__page - 2, params)
        if self.__page - 1 > 0:
            page1_left = '<a href="{0}{1}/{2}">{1}</a>'.format(url, self.__page - 1, params)
        
        if self.__page + 2 <= self.__count_pages:
            page2_right = '<a href="{0}{1}/{2}">{1}</a>'.format(url, self.__page + 2, params)
        
        if self.__page + 1 <= self.__count_pages:
            page1_right = '<a href="{0}{1}/{2}">{1}</a>'.format(url, self.__page + 1, params)
        
        current_page = '<a href="#">{0}</a>'.format(self.__page)
        
        text = '''<ul class="pagination">
<li>{}</li>
<li>{}</li>
<li>{}</li>
<li class="active">{}</li>
<li>{}</li>
<li>{}</li>
<li>{}</li>
</ul>'''.format(
            first_page, page2_left, page1_left, current_page, page1_right, page2_right, next_page)
        return text
        
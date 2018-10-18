from flask import url_for

class MenuPage:
    def __init__(self, caption, *args):
        self.caption = caption # Название страницы
        self.__pages = args # Список всех страниц в текущей позиции
        self.page = self.__pages[0] # ссылка в меню
    
    def startswith(self, current_page):
        ''' Проверка есть ли страница '''
        for page in self.__pages:
            if current_page.startswith(page):
                return True
        return False
    
    def match(self, current_page):
        ''' Сравнение страницы '''
        for page in self.__pages:
            if current_page == page:
                return True
        return False
 
class Menu:
    def __init__(self):
        self.pages = []
    def append(self, caption, *args):
        ''' Добавляем страницы в меню '''
        self.pages.append(MenuPage(caption, *args))

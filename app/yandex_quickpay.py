#!/usr/bin/env python3
import urllib.parse
from hashlib import sha1
from flask import redirect
from . import app

class YandexMoney:
    def __init__(self, label, sum_value):
        self.values = {
            'receiver': app.config['YANDEX_MONEY_RECEIVER'],
            'quickpay-form': app.config['YANDEX_MONEY_QUICKPAY_FORM'],
            'successURL': app.config['YANDEX_MONEY_SUCCESS_URL'],
            'formcomment': app.config['YANDEX_MONEY_FORMCOMMENT'],
            'short-dest': app.config['YANDEX_MONEY_SHORT_DEST'],
            'targets': app.config['YANDEX_MONEY_TARGETS'],
            'paymentType': app.config['YANDEX_MONEY_PAYMENT_TYPE'],
            'label' : label,
            'sum' : sum_value
        }
    
    def redirect(self):
        data = urllib.parse.urlencode(self.values)
        return redirect('https://money.yandex.ru/quickpay/confirm.xml?{}'.format(data))
    
    

class YandexMoneyHash:
    def __init__(self, query, secret=None):
        self.secret = secret or app.config['YANDEX_MONEY_HASH_SECRET']
        self.query = query
        self.hash_str = self.make_hash_str()
        
        
    def make_hash_str(self):
        keys = ['notification_type', 'operation_id', 'amount',
                'currency', 'datetime', 'sender', 'codepro', 'label']
        hash_str = ''
        for key in keys:
            if key in self.query:
                value = self.query[key]
                if key == 'label':
                    hash_str += self.secret + '&' + value
                    continue
                hash_str += value + '&'
        return hash_str
    
    def make(self):
        return sha1(bytes(self.hash_str, 'utf-8')).hexdigest()

    def check(self):
        if 'sha1_hash' in self.query:
            return self.make() == self.query['sha1_hash']
        return False
        
    
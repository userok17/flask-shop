#!/usr/bin/env python3

import unittest
from app import app, db
from app.models import User, Product

class BasicsTestCase(unittest.TestCase):
    # def test_user(self):
    #     user = User.query.filter_by(id=None).first()
    #     self.assertTrue(user is None)
    def test_filename(self):
        product = Product.query.filter_by(id=6).first()
        self.assertTrue(product.image is None)
    
        

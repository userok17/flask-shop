#!/usr/bin/env python3
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from app import manager

if __name__ == '__main__':
    manager.run()


    
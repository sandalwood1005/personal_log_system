import sys
import os

path = '/home/tantantan/mysite'
if path not in sys.path:
    sys.path.append(path)

os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = '2ac6a020a645fc64b9bfd27f7dbd59f26f9bb9649bc9290d0d6f626c1f0a7dc5'

from app import app as application

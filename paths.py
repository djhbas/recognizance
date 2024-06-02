import sys
import os

from instagrapi import Client


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


home = os.path.expanduser('~')
resource_add = os.path.join(home, 'resource')
data_add = os.path.join(home, 'resource\\data')
tmp_add = os.path.join(home, 'resource\\tmp')
img_add = os.path.join(home, 'resource\\img')

LOCOUT = resource_path('resource\\ui\\locout.ui')
LOGIN = resource_path('resource\\ui\\login.ui')
MAINW = resource_path('resource\\ui\\mainw.ui')
USER_JSON = os.path.join(home, 'resource\\tmp\\user.json')
DUMP_JSON = os.path.join(home, 'resource\\tmp\\dump.json')
USERS_CSV = os.path.join(home, 'resource\\data\\users.csv')
POSTS_CSV = os.path.join(home, 'resource\\data\\posts.csv')
JOB = os.path.join(home, 'resource\\tmp\\decision_tree.joblib')
MODEL = resource_path('resource\\tmp\\nn_model.h5')
MAP_HTML = os.path.join(home, 'resource\\img\\map.html')
MAP_PNG = os.path.join(home, 'resource\\img\\map.png').replace('\\', '/')
MAP = 'map.png'
KEY = os.path.join(home, 'resource\\tmp\\filekey.key')
HND_BLACK = 'HelveticaNowDisplay Black'
HND_REG = 'HelveticaNowDisplay Regular'
HND_LIGHT = 'HelveticaNowDisplay Light'
HND_BOLD = 'HelveticaNowDisplay Bold'
USERNAME = None
PASSWORD = None

cl = Client(request_timeout=7)

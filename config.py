import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xc6\xcfn\x07-\xabs7\xf7\xe9\xe3xl]\x1a\x93'

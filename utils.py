# python lib
import os
import hashlib

# custom lib
from storage import Storage

def resolve_to_cwd(relative_path):
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    data_file = os.path.join(path, relative_path)
    return data_file

def calc_param_sign(msg:str):
    text = msg + Storage.bili['app_secret']
    hashed = hashlib.md5(text.encode('utf-8'))
    return hashed.hexdigest()

def parse_param(params:dict):
    parsed = ''
    for key in sorted(params.keys()):
        if params[key] != '':
            parsed += key + '=' + params[key] + '&'
    else:
        parsed = parsed[:-1]
    return parsed


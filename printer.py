# python lib
import os
import sys
import time
import colorama

# custom lib
import utils

class ColorPrinter:

    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(ColorPrinter, cls).__new__(cls, *args, **kwargs)
            inst = cls.instance
            colorama.init()
            inst.COLOR_CODE = {
                'default': '\033[0m',
                'red':     '\033[31m',
                'green':   '\033[32m',
                'yellow':  '\033[33m',
                'blue':    '\033[34m',
                'purple':  '\033[35m',
                'cyan':    '\033[36m',
                'white':   '\033[37m',
            }
        return cls.instance

def current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def cprint(*args, color='default', target=None, error=None, **kwargs):
    cp = ColorPrinter()
    color = 'default' if color.lower() not in cp.COLOR_CODE else color.lower()
    color = 'red' if error else color
    c = cp.COLOR_CODE[color]

    text = ''
    text += c
    text += f'[{current_time()}]    '
    text += ' '.join(args)
    text += cp.COLOR_CODE['default']

    if target is None:
        if error:
            sys.stderr.write(f'{text}\n', **kwargs)
        else:
            print(text, **kwargs)
    else:
        data_file = utils.resolve_to_cwd(target)
        with open(data_file, 'a') as iofile:
            iofile.write(text + '\n')

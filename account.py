# python lib
from ruamel.yaml import YAML

# custom lib
import utils
from printer import cprint


class Account:

    def __init__(self, input_file, yaml=None):
        yaml = yaml if yaml is not None else YAML()
        self.yaml = yaml

        self.username = None
        self.password = None
        self.web_cookies = None
        self.app_cookies = None
        self.uid = 0
        self.input_file = input_file
        self.banned = False

        data_file = utils.resolve_to_cwd(input_file)
        try:
            with open(data_file, 'r') as iofile:
                store = self.yaml.load(iofile)
            
            self.username = store.get('user').get('username')
            self.password = store.get('user').get('password')
            self.web_cookies = store.get('web')
            self.app_cookies = store.get('app')
            try:
                self.uid = self.web_cookies.get('DedeUserID')
            except AttributeError:
                pass
        except FileNotFoundError:
            msg = (f'File {self.input_file!r} not found. Skipped')
            cprint(f'{msg}', error=True)
        except (TypeError, AttributeError):
            pass
    
    def cprint(self, *args, color='default', **kwargs):
        prefix = f'[{self.uid}]'
        data = ' '.join(args)
        cprint(f'{prefix:<13} {data}', color=color, **kwargs)

    @property
    def usable(self):
        usable = False
        try:
            usable = self.web_cookies and all([ cookie for cookie in self.web_cookies.values() ])
        except AttributeError:
            cprint(f'AttributeError in account.py', error=True)
        return usable

    

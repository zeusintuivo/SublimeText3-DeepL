# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv   # Need to install  pip3 install -U python-dotenv  and pip install -U python-dotenv
# import xml.etree.ElementTree as et

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')
print('Settings:', dotenv_path)
# Load file from the path.
load_dotenv(dotenv_path)


class Settings(object):

    @property
    def settings(self):
        # Accessing variables.
        # print(settings()['source_language'])
        # Using variables.
        return {'source_language': os.getenv('source_language'),
                'target_language': os.getenv('target_language'),
                'keep_moving_down': os.getenv('keep_moving_down'),
                'target_type': os.getenv('target_type'),
                'auth_key': os.getenv('auth_key'),
                'proxy_enable': os.getenv('proxy_enable'),
                'proxy_type': os.getenv('proxy_type'),
                'proxy_host': os.getenv('proxy_host'),
                'proxy_port': os.getenv('proxy_port')}
        # root = et.fromstring(data)
        # return root


def settings_list():
    # Accessing variables.
    # [source_language, target_language, keep_moving_down, target_type, auth_key, proxy_enable, proxy_type, proxy_host,
    # proxy_port] = settings()
    # Using variables.
    return [os.getenv('source_language'),
            os.getenv('target_language'),
            os.getenv('keep_moving_down'),
            os.getenv('target_type'),
            os.getenv('auth_key'),
            os.getenv('proxy_enable'),
            os.getenv('proxy_type'),
            os.getenv('proxy_host'),
            os.getenv('proxy_port')]


def test_settings_list():
    [source_language, target_language, keep_moving_down, target_type, auth_key, proxy_enable, proxy_type, proxy_host,
     proxy_port] = settings_list()
    print(proxy_enable)

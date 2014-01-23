import pdb
import logging
import requests

from django.conf import settings

def log_error(module, ex):
    template = "An exception of type {0} occurred in {1}. Arguments:\n{2!r}"
    message = template.format(type(ex).__name__, module, ex.args)
    logging.info(message)
    return message

def request_key_from_handcar(user, host):
    key_var = host.upper().split('.')[0].replace('-', '_') + '_KEY'
    my_key = getattr(settings, key_var)
    agent = user.email
    gen_key_url = 'https://' + host + '/handcar/services/authentication/agentkeys/' + \
                  agent + '/?proxyname=' + my_key
    cxn = requests.get(gen_key_url)
    agent_key = cxn.text
    return agent_key
    # return my_key
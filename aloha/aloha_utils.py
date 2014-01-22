import pdb
import logging
import requests

from django.conf import settings

def log_error(module, ex):
    template = "An exception of type {0} occurred in {1}. Arguments:\n{2!r}"
    message = template.format(type(ex).__name__, module, ex.args)
    logging.info(message)
    return message

def request_key_from_handcar(user):
    mc3 = settings.MC3_HOST
    my_key = settings.MC3_KEY
    agent = user.email
    gen_key_url = 'https://' + mc3 + '/handcar/services/authentication/agentkeys/' + \
                  agent + '/?proxyname=' + my_key
    cxn = requests.get(gen_key_url)
    agent_key = cxn.text
    # agent_key = settings.MC3_KEY
    return agent_key
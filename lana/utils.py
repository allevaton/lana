# Shareable utilities
#
#

import json
import warnings


def class2json(c, stringify=False):
    warnings.warn('This method should not be used, '
                  'we are not using Class objects anymore', DeprecationWarning)
    d = vars(c)
    return json.dumps(d) if stringify else d


def dict_safe_update(d, new):
    for k, v in new.items():
        if not d.get(k):
            d[k] = v

    return d


def validate_response(response, fail_text):
    if response.status_code != 200:
        raise ConnectionError('%d: %s' % (response.status_code, fail_text))

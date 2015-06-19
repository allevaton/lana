# Shareable utilities
#
#

import json


def class2json(c, stringify=False):
    d = vars(c)
    return json.dumps(d) if stringify else d

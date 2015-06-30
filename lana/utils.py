# Shareable utilities
#
#


def dict_safe_update(d, new):
    for k, v in new.items():
        if not d.get(k):
            d[k] = v

    return d


def validate_response(response, fail_text):
    if response.status_code != 200:
        raise ConnectionError('%d: %s' % (response.status_code, fail_text))

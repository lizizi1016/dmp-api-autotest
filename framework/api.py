import requests

import sys

this = sys.modules[__name__]
this.login_fn = None
this.token = None


def api_set_login_fn(fn):
    this.login_fn = fn


def api_get_response(context, r=None):
    if r is None:
        return context.r.json()
    else:
        return r.json()


def api_get(context, url_path_segment, params=None):
    r = api_request_op("get", context, url_path_segment, True, params)
    assert r.status_code == 200
    return api_get_response(context, r)


def api_post(context, url_path_segment, params=None):
    r = api_request_op("post", context, url_path_segment, True, params)
    assert r.status_code == 200
    return api_get_response(context, r)


def api_request_get(context, url_path_segment, params=None):
    r = api_request_op("get", context, url_path_segment, True, params)
    context.r = r
    return r


def api_request_post(context, url_path_segment, params=None):
    r = api_request_op("post", context, url_path_segment, True, params)
    context.r = r
    return r


def api_request_op(op,
                   context,
                   url_path_segment,
                   try_login_if_need,
                   params=None):
    url = context.base_url + url_path_segment

    if context == params:
        params = {}
        for row in context.table:
            for x in context.table.headings:
                params[x] = row[x]
                if row[x].startswith("context"):
                    params[x] = eval(row[x])

    headers = {}
    if this.token != None:
        headers = {"authorization": this.token}

    r = getattr(requests, op)(url, params, headers=headers)
    api_log_full(r)

    if try_login_if_need and r.status_code == 401 and login_fn != None:
        this.token = None
        token = login_fn(context)
        this.token = token
        return api_request_op(op, context, url_path_segment, False, params)
    else:
        return r


def api_log_full(r):
    req = r.request
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".
    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """

    print("")
    print("")

    print('{}\n{}\n{}\n\n{}'.format(
        '-----------REQUEST-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

    print("")

    print('{}\n{}\n{}\n\n{}'.format(
        '-----------RESPONSE-----------',
        str(r.status_code) + ' ' + r.reason,
        '\n'.join('{}: {}'.format(k, v) for k, v in r.headers.items()),
        r.text,
    ))
    print("")

    print('Operation took ' + str(round(r.elapsed.total_seconds(), 3)) + 's')

    print("")
    print("")
    print("")
    print("")

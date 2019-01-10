import requests

def api_request_get(context, url_path_segment):
    #url = context.base_url + '/' + url_path_segment
    url = 'http://10.186.62.2:25799/v3/' + url_path_segment
    # context.r = requests.get(url, headers=context.headers)
    context.r = requests.get(url)
    api_log_full(context.r)
    return context.r

def api_get_response(context):
    return context.r.json()

def api_get(context, url_path_segment, params=None):
    url = 'http://10.186.62.2:25799/v3/' + url_path_segment

    if context == params:
        params = {}
        for row in context.table:
            for x in context.table.headings:
                params[x] = row[x]
                if row[x].startswith("context"):
                    params[x] = eval(row[x])

    r = requests.get(url, params)
    api_log_full(r)
    return r.json()

def api_post(context, url_path_segment, params=None):
    url = 'http://10.186.62.2:25799/v3/' + url_path_segment

    if context == params:
        params = {}
        for row in context.table:
            for x in context.table.headings:
                params[x] = row[x]
                if row[x].startswith("context"):
                    params[x] = eval(row[x])
    
    context.r = requests.post(url, params)
    api_log_full(context.r)
    return context.r

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
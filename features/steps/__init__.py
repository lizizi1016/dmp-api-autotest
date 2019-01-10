from behave import *
import parse

@parse.with_pattern(r"[^\s]+[\s,]*")
def parse_strings(text):
    return text.strip(" ,")

register_type(strings=parse_strings)

@parse.with_pattern(r"[^\s]+")
def parse_string(text):
    return text.strip()

register_type(string=parse_string)

@step('I set base URL to "{base_url}"')
def set_base_url(context, base_url):
    if base_url.startswith("context"):
        context.base_url = getattr(context, base_url[8:])
    else:
        context.base_url = base_url.encode('ascii')

@then(u'the response is ok')
def step_impl(context):
    assert context.r.status_code == 200
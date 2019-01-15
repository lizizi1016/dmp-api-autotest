from behave import *
import parse

@parse.with_pattern(r"[^\s]+")
def parse_strings(text):
    return text.strip(" ,")

register_type(strings=parse_strings)

@parse.with_pattern(r"[^\s]+")
def parse_string(text):
    return text.strip()

register_type(string=parse_string)

@parse.with_pattern(r"[\d]+")
def parse_int(text):
    return int(text)

register_type(int=parse_int)

@parse.with_pattern(r"s")
def parse_s(text):
    return text

register_type(s=parse_s)

@parse.with_pattern(r"[\d]+s")
def parse_time(text):
    return int(text.strip("s"))

register_type(time=parse_time)

@step('I set base URL to "{base_url}"')
def set_base_url(context, base_url):
    if base_url.startswith("context"):
        context.base_url = getattr(context, base_url[8:])
    else:
        context.base_url = base_url.encode('ascii')

@then(u'the response is ok')
def step_impl(context):
    assert context.r.status_code == 200
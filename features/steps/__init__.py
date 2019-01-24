from behave import *
from framework.api import *
import parse

@parse.with_pattern(r"should( not)?")
def parse_should_or_not(text):
    if text == "should not":
        return False
    else:
        return True
        
register_type(should_or_not=parse_should_or_not)

@parse.with_pattern(r"[^\s]+")
def parse_strings(text):
    return text.strip(" ,")

register_type(strings=parse_strings)

@parse.with_pattern(r"[^\s]+")
def parse_string(text):
    return text.strip()

register_type(string=parse_string)

@parse.with_pattern(r".*")
def parse_any(text):
    return text.strip()

register_type(any=parse_any)

@parse.with_pattern(r"[\d]+")
def parse_int(text):
    return int(text)

register_type(int=parse_int)

@parse.with_pattern(r"s")
def parse_s(text):
    return text

register_type(s=parse_s)

@parse.with_pattern(r"[\d]+[sm]")
def parse_time(text):
    num = int(text.strip("sm"))
    if text[-1] == 'm':
        return num*60
    else:
        return num

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

def login(context):
    resp = api_post(context, "user/login", {
        "user": "admin",
        "password": "admin",
    })
    return resp["token"]

api_set_login_fn(login)

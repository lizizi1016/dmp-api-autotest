from behave import *
from framework.api import *
import pyjq

use_step_matcher("cfparse")


@when(u'I add a RTO templates, {template_values:option_values}')
def step_impl(context, template_values):
    template_params = {
        "name": template_values['name'],
        "sla_rto": template_values['sla_rto'],
        "sla_rto_levels": template_values['sla_rto_levels'],
        "sla_rto_te": "500",
        "sla_type": template_values['type']
    }
    api_post(context, "sla/add", template_params)


@Then(u'assert create RTO templates succeed, {template_values:option_values}')
def step_impl(context, template_values):
    resp = api_get(context, '/sla/list')
    conditions = '.[] | select(."name"=="' + template_values['name'] + '") | select (."sla_rto_levels"=="' + \
                 template_values['sla_rto_levels'] + '") | select(."sla_rto"=="' + template_values[
                     'sla_rto'] + '") | select(."sla_type"=="' + template_values['type'] + '")'
    match = pyjq.first(conditions, resp)
    if match is not None:
        assert True
    else:
        print("Create RTO template failed !")
        assert False

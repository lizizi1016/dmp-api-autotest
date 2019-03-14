from behave import *
from framework.api import *
import pyjq
import time
import json
import re
from util import *
from common import *

use_step_matcher("cfparse")


@when(u'I add {type:string} alert channel')
def step_imp(context, type):
    if type == "smtp":
        config = {
            "name":
            "smtp",
            "universe_configs": [{
                "send_resolved": True,
                "type": "smtp",
                "smtp_addr": "smtp.exmail.qq.com",
                "smtp_port": 465,
                "smtp_ssl": True,
                "smtp_user": "tester@actionsky.com",
                "smtp_password": "CGPKPhYAgnAJw2tZ",
                "smtp_from": "dmp_test@163.com ",
                "smtp_tos": "dmp_test@163.com ",
                "desc": "test_smtp"
            }]
        }
        resp = api_get(context, "alert/list_alert", {
            "number": context.page_size_to_select_all,
        })
        res = resp.replace("\/", "")
        alert_info = json.loads(res)
        alert_info['receivers'].append(config)
        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)

    elif type == "wechat":
        config = {
            "name":
            "wechat",
            "universe_configs": [{
                "send_resolved": True,
                "type": "wechat",
                "wechat_corpid": "wx0a593f2cdb0b487f",
                "wechat_corpsecret":
                "G6kAsnnU_EAflXKHxE5_h6iPp0ydf3S69WzSP20eF03evkBj6tfHFDFiiVrBhwT2",
                "wechat_agentid": 1,
                "wechat_safe": 1,
                "wechat_proxy": "",
                "wechat_touser": "13812069570",
                "wechat_toparty": "",
                "wechat_totag": "",
                "desc": "test_wechat"
            }]
        }

        resp = api_get(context, "alert/list_alert", {
            "number": context.page_size_to_select_all,
        })
        res = resp.replace("\/", "")
        alert_info = json.loads(res)
        alert_info['receivers'].append(config)
        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)


@then(
    u'the alert channel list {should_or_not:should_or_not} contains the {type:string} alert channel'
)
def step_imp(context, should_or_not, type):
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    match = pyjq.first('.|.receivers|any(."name" == "{0}")'.format(type),
                       json.loads(res))
    assert (match is not False and should_or_not) or (match is not True and
                                                      not should_or_not)


@when(u'I found a valid the {type:string} alert channel, or I skip the test')
def step_imp(context, type):
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    match = pyjq.first('.|.receivers[]|select(."name" == "{0}")'.format(type),
                       json.loads(res))
    if match is None:
        context.scenario.skip("No valid {0} alert channel".format(type))
        return
    if type == "smtp":
        context.alert_channel = match
    else:
        context.alert_channel = match


@when(u'I update the {type:string} alert channel')
def step_imp(context, type):
    assert context.alert_channel != None
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    alert_info = json.loads(res)
    if type == "smtp":
        config = context.alert_channel
        alert_info['receivers'].remove(config)
        config['universe_configs'][0]['desc'] = "smtp_update"
        alert_info['receivers'].append(config)

        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)
    elif type == "wechat":
        config = context.alert_channel
        alert_info['receivers'].remove(config)
        config['universe_configs'][0]['desc'] = "wechat_update"
        alert_info['receivers'].append(config)

        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)


@then(u'the {type:string} alert channel should be updated')
def step_imp(context, type):
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    if type == "smtp":
        match = pyjq.first(
            '.|.receivers[]|select(."name" == "smtp")|.universe_configs|any(."desc" == "smtp_update")',
            json.loads(res))
        assert match is not False
    elif type == "wechat":
        match = pyjq.first(
            '.|.receivers[]|select(."name" == "wechat")|.universe_configs|any(."desc" == "wechat_update")',
            json.loads(res))
        assert match is not False


@when(u'I remove the {type:string} alert channel')
def step_imp(context, type):
    assert context.alert_channel != None
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    alert_info = json.loads(res)
    if type == "smtp":
        config = context.alert_channel
        alert_info['receivers'].remove(config)

        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)
    elif type == "wechat":
        config = context.alert_channel
        alert_info['receivers'].remove(config)

        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)


@when(u'I add the {type:string} alert configuration')
def step_imp(context, type):
    assert context.alert_channel != None
    if type == "smtp":
        smtp_config = {
            "route_id":
            "6",
            "is_expression_match":
            True,
            "match_exp":
            "",
            "receiver":
            "smtp",
            "group_by": [
                "code", "level", "src_comp_type", "alert_comp_id",
                "alert_comp_type", "server", "app_name", "src_comp_id"
            ],
            "group_wait":
            5000000000,
            "repeat_interval":
            3600000000000,
            "group_interval":
            3600000000000,
            "continue":
            True,
            "routes": []
        }
        resp = api_get(context, "alert/list_alert", {
            "number": context.page_size_to_select_all,
        })
        res = resp.replace("\/", "")
        alert_info = json.loads(res)
        alert_info['route']['routes'].append(smtp_config)
        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)
    elif type == "wechat":
        wechat_config = {
            "route_id":
            "9",
            "is_expression_match":
            True,
            "match_exp":
            "",
            "receiver":
            "wechat",
            "group_by": [
                "code", "level", "src_comp_id", "src_comp_type",
                "alert_comp_id", "alert_comp_type", "server", "app_name"
            ],
            "group_wait":
            5000000000,
            "repeat_interval":
            3600000000000,
            "group_interval":
            3600000000000,
            "continue":
            True,
            "routes": []
        }
        resp = api_get(context, "alert/list_alert", {
            "number": context.page_size_to_select_all,
        })
        res = resp.replace("\/", "")
        alert_info = json.loads(res)
        alert_info['route']['routes'].append(wechat_config)
        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)


@then(
    u'the {type:string} alert configuration list {should_or_not:should_or_not} contains the alert configuration'
)
def step_imp(context, should_or_not, type):
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    match = pyjq.first(
        '.|."route"|."routes"|any(."receiver" == "{0}")'.format(type),
        json.loads(res))
    assert (match is not False and should_or_not) or (match is not True and
                                                      not should_or_not)


@when(
    u'I found a valid the {type:string} alert configuration, or I skip the test'
)
def step_imp(context, type):
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    match = pyjq.first(
        '.|."route"|.routes[]|select(."receiver" == "{0}")'.format(type),
        json.loads(res))
    if match is None:
        context.scenario.skip("No valid {0} alert configuration".format(type))
        return
    if type == "smtp":
        context.alert_configuration = match
    else:
        context.alert_configuration = match


@when(u'I update the {type:string} alert configuration')
def step_imp(context, type):
    assert context.alert_configuration != None
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    alert_info = json.loads(res)
    if type == "smtp":
        config = context.alert_configuration
        alert_info['route']['routes'].remove(config)
        config['group_wait'] = 1000000000
        config["repeat_interval"] = 12000000000
        config["group_interval"] = 12000000000
        config["continue"] = False
        alert_info['route']['routes'].append(config)

        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)
    elif type == "wechat":
        config = context.alert_configuration
        alert_info['route']['routes'].remove(config)
        config['group_wait'] = 1000000000
        config["repeat_interval"] = 12000000000
        config["group_interval"] = 12000000000
        config["continue"] = False
        alert_info['route']['routes'].append(config)

        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)


@then(u'the {type:string} alert configuration should be updated')
def step_imp(context, type):
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    if type == "smtp":
        match = pyjq.first(
            '.|."route"|.routes[]|select(."receiver" == "{0}")'.format(type),
            json.loads(res))
        assert match is not None

    elif type == "wechat":
        match = pyjq.first(
            '.|."route"|.routes[]|select(."receiver" == "{0}")'.format(type),
            json.loads(res))
        assert match is not None


@when(u'I remove the {type:string} alert configuration')
def step_imp(context, type):
    assert context.alert_configuration != None
    resp = api_get(context, "alert/list_alert", {
        "number": context.page_size_to_select_all,
    })
    res = resp.replace("\/", "")
    alert_info = json.loads(res)
    if type == "smtp":
        config = context.alert_configuration
        alert_info['route']['routes'].remove(config)
        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)
    elif type == "wechat":
        config = context.alert_configuration
        alert_info['route']['routes'].remove(config)
        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)


@when(u'I add the {type:string} alert configuration subkey')
def step_imp(context, type):
    assert context.alert_configuration != None
    if type == "smtp":
        smtp_config = {
            "routes": [{
                "route_id":
                "10",
                "is_expression_match":
                True,
                "match_exp":
                "",
                "receiver":
                "smtp",
                "group_by": [
                    "code", "level", "src_comp_id", "src_comp_type",
                    "alert_comp_id", "alert_comp_type", "server", "app_name"
                ],
                "group_wait":
                5000000000,
                "repeat_interval":
                3600000000000,
                "group_interval":
                3600000000000,
                "continue":
                True,
                "routes": []
            }]
        }
        resp = api_get(context, "alert/list_alert", {
            "number": context.page_size_to_select_all,
        })
        res = resp.replace("\/", "")
        alert_info = json.loads(res)
        alert_info['route']['routes'].append(smtp_config)
        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)
    elif type == "wechat":
        wechat_config = {
            "routes": [{
                "route_id":
                "22",
                "is_expression_match":
                True,
                "match_exp":
                "",
                "receiver":
                "wechat",
                "group_by": [
                    "code", "level", "src_comp_id", "src_comp_type",
                    "alert_comp_id", "alert_comp_type", "server", "app_name"
                ],
                "group_wait":
                5000000000,
                "repeat_interval":
                3600000000000,
                "group_interval":
                3600000000000,
                "continue":
                True,
                "routes": []
            }]
        }
        resp = api_get(context, "alert/list_alert", {
            "number": context.page_size_to_select_all,
        })
        res = resp.replace("\/", "")
        alert_info = json.loads(res)
        alert_info['route']['routes'].append(wechat_config)
        body = {"is_sync": True, "alert_config": json.dumps(alert_info)}
        api_request_post(context, "/alert/save_alert", body)

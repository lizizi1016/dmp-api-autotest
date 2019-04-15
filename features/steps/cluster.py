from behave import *
from framework.api import *
import pyjq
import time
import json
import re
from util import *
from common import *

@when(u'I init DMP')
def step_impl(context):
    localsys = api_get(context, "support/localsys")
    hostname = localsys["hostname"]
    ip = localsys["sip"]

    ucore = api_get(context, "support/component?pattern=ucore")[-1]["Name"]
    uagent = api_get(context, "support/component?pattern=uagent")[-1]["Name"]
    ustats = api_get(context, "support/component?pattern=ustats")[-1]["Name"]
    udeploy = api_get(context, "support/component?pattern=udeploy")[-1]["Name"]
    mysql = api_get(context, "support/component?pattern=mysql")[-1]["Name"]

    api_post(context, "install/umc", {
        "is_sync": True,
        "component_path": "/opt",
        "server_id": "server-" + hostname,
        "server_ip": ip,
        "hostname": hostname,
        "ucore_path": "/opt/ucore",
        "ucore_install_file": ucore,
        "ucore_id": "ucore-" + hostname,
        "uagent_path": "/opt/uagent",
        "uagent_install_file": uagent,
        "uagent_id": "uagent-" + hostname,
        "udeploy_path": "/opt/udeploy",
        "udeploy_install_file": udeploy,
        "udeploy_id": "udeploy-" + hostname,
        "ustats_path": "/opt/ustats",
        "ustats_install_file": ustats,
        "ustats_id": "ustats-" + hostname,
        "umc_path": "/opt/umc",
        "umc_id": "umc-" + hostname,
        "mysql_tarball_path": mysql,
        "mysql_path": "/opt/udb/mysql",
        "mysql_port": "5690",
        "initial_mgr_port": "5691",
        "mysql_id": "mysql-udb1",
        "version": "5.7.20",
        "install_standard": "semi_sync"
    })

    uguard_mgr = api_get(context, "support/component?pattern=uguard-mgr")[-1]["Name"]
    api_post(context, "server/install", {
        "is_sync": True,
        "server_id": "server-" + hostname,
        "component": "uguard-mgr",
        "uguard-mgr_path": "/opt/uguard-mgr",
        "uguard-mgr_id": "uguard-mgr-" + hostname,
        "uguard-mgr_install_file": uguard_mgr
    })

    umon = api_get(context, "support/component?pattern=umon")[-1]["Name"]
    api_post(context, "server/install", {
        "is_sync": True,
        "server_id": "server-" + hostname,
        "component": "umon",
        "umon_path": "/opt/umon",
        "umon_id": "umon-" + hostname,
        "umon_install_file": umon
    })

    urman_mgr = api_get(context, "support/component?pattern=urman-mgr")[-1]["Name"]
    api_request_post(context, "server/install", {
        "is_sync": True,
        "server_id": "server-" + hostname,
        "component": "urman-mgr",
        "urman-mgr_path": "/opt/urman-mgr",
        "urman-mgr_id": "urman-mgr-" + hostname,
        "urman-mgr_install_file": urman_mgr
    })


@when(u'I add server from parameter')
def step_impl(context):
    assert context.new_server_ip != None
    assert context.new_server_ssh_port != None
    assert context.new_server_ssh_user != None
    assert context.new_server_ssh_password != None

    hostname = api_get(context, "support/hostname", {
        "ip": context.new_server_ip,
        "port": context.new_server_ssh_port,
        "user": context.new_server_ssh_user,
        "password": context.new_server_ssh_password,
    })
    hostname = hostname.strip()

    uagent = api_get(context, "support/component?pattern=uagent")[-1]["Name"]
    ustats = api_get(context, "support/component?pattern=ustats")[-1]["Name"]

    api_request_post(context, "server/add", {
        "is_sync": True,
        "uagent_install_method": "ssh",
        "server_ip": context.new_server_ip,
        "ssh_port": context.new_server_ssh_port,
        "ssh_user": context.new_server_ssh_user,
        "ssh_password": context.new_server_ssh_password,
        "hostname": hostname,
        "server_id": "server-" + hostname,
        "uagent_path": "/opt/uagent",
        "uagent_id": "uagent-" + hostname,
        "uagent_install_file": uagent,
        "ustats_path": "/opt/ustats",
        "ustats_id": "ustats-" + hostname,
        "ustats_install_file": ustats,
    })


@when(u'I install Udeploy,Uguard-agent,Urman-agent on all server')
def step_impl(context):
    while True:
        context.execute_steps(u"""
                When I found a server without component uguard-agent, or I skip the test
            """)
        if context.server is None:
            break
        context.execute_steps(u"""
                When I prepare the server for uguard
                Then the response is ok
            """)


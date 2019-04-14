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

    api_request_post(context, "install/umc", {
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

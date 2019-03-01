from behave import *
from framework.api import *
import pyjq
import time
import json
import re
from util import *
from common import *

use_step_matcher("cfparse")


@when(u'I found a running MySQL instance, or I skip the test')
def step_impl(context):
    resp = api_get(context, "database/list_group", {
        "number": context.page_size_to_select_all,
    })
    match = pyjq.first('.data[] | select(.group_instance_num == "1")', resp)
    if match is None:
        context.scenario.skip("Found no MySQL instance")
        return
    mysqls = api_get(context, "database/list_instance", {
        "number": context.page_size_to_select_all,
    })
    mysql = pyjq.first(
        '.data[] | select(.mysql_status == "STATUS_MYSQL_HEALTH_OK" and .group_id == "{0}" )'
        .format(match['group_id']), mysqls)
    if mysql is None:
        context.scenario.skip("Found no MySQL instance without backup rule")
        return
    else:
        root_password = api_get(context, "helper/get_mysql_password", {
            "mysql_id": mysql["mysql_id"],
            "password_type": "ROOT",
        })
        mysql["root_password"] = root_password
        context.mysql_instance = mysql


@when(u'I query the MySQL instance "{query:any}"')
def step_impl(context, query):
    assert context.mysql_instance != None
    mysql = context.mysql_instance

    resp = api_get(
        context, "helper/query_mysql", {
            "mysql_id": mysql["mysql_id"],
            "query": query,
            "user": "root",
            "password": mysql["root_password"],
        })
    context.mysql_resp = resp


@then(u'the MySQL response should be')
def step_impl(context):
    assert context.mysql_resp != None
    resp = context.mysql_resp

    idx = 0
    for row in context.table:
        actual_row = resp[idx]
        for heading in context.table.headings:
            assert row[heading] == actual_row[heading]
        idx += 1


@when(u'I add a MySQL group with the SIP')
def step_impl(context):
    assert context.valid_sip != None
    sip = context.valid_sip

    mysql_group_id = "mysql-group-" + generate_id()

    api_request_post(context, "database/add_group", {
        "is_sync": True,
        "group_id": mysql_group_id,
        "sip": sip,
        "tag_list": "[]",
    })

    context.mysql_group = {"group_id": mysql_group_id}


@when(u'I add a MySQL group')
def step_impl(context):
    mysql_group_id = "mysql-group-" + generate_id()

    api_request_post(context, "database/add_group", {
        "is_sync": True,
        "group_id": mysql_group_id,
        "tag_list": "[]",
    })

    context.mysql_group = {"group_id": mysql_group_id}


@then(
    u'the MySQL group list {should_or_not:should_or_not} contains the MySQL group'
)
def step_impl(context, should_or_not):
    assert context.mysql_group != None
    mysql_group_id = context.mysql_group["group_id"]

    resp = api_get(context, "database/list_group", {
        "number": context.page_size_to_select_all,
    })
    match = pyjq.first(
        '.data[] | select(.group_id == "{0}")'.format(mysql_group_id), resp)
    assert (match != None and should_or_not) or (match == None and
                                                 not should_or_not)


@when(
    u'I found a MySQL group without MySQL instance, and without SIP, or I skip the test'
)
def step_impl(context):
    resp = api_get(context, "database/list_group", {
        "number": context.page_size_to_select_all,
    })
    match = pyjq.first(
        '.data[] | select(.group_instance_num == "0") | select(has("sip") | not)',
        resp)
    if match is None:
        context.scenario.skip(
            "Found no MySQL group without MySQL instance, and without SIP")
    else:
        context.mysql_group = match


@when(u'I found a MySQL group without MySQL instance, or I skip the test')
def step_impl(context):
    resp = api_get(context, "database/list_group", {
        "number": context.page_size_to_select_all,
    })
    match = pyjq.first('.data[] | select(.group_instance_num == "0")', resp)
    if match is None:
        context.scenario.skip("Found no MySQL group without MySQL instance")
    else:
        context.mysql_group = match


@when(u'I remove the MySQL group')
def step_impl(context):
    assert context.mysql_group != None
    mysql_group_id = context.mysql_group["group_id"]

    api_request_post(context, "database/remove_group", {
        "is_sync": True,
        "group_id": mysql_group_id,
    })


@when(u'I add MySQL instance in the MySQL group')
def step_impl(context):
    assert context.mysql_group != None
    assert context.valid_port != None
    assert context.server != None
    mysql_group_id = context.mysql_group["group_id"]
    mysql_id = "mysql-" + generate_id()
    mysql_dir = context.mysql_installation_dir
    port = context.valid_port
    install_file = get_mysql_installation_file(context)
    version = re.match(r".*(\d+\.\d+\.\d+).*", install_file).group(1)
    main_version = re.match(r"(\d+\.\d+)\.\d+", version).group(1)

    mycnf = api_get(context, "support/read_umc_file", {
        "path": "mycnfs/my.cnf." + main_version,
    })

    mycnf = mycnf.replace("innodb_data_file_path = ibdata1:1G:autoextend",
                          "innodb_data_file_path = ibdata1:64M:autoextend")

    install_params = {
        "server_id": context.server["server_id"],
        "group_id": context.mysql_group["group_id"],
        "port": port,
        "mysql_id": mysql_id,
        "mysql_alias": mysql_id,
        "mysql_tarball_path": install_file,
        "install_standard": "uguard_semi_sync",
        "init_data": "",
        "create_extranet_root": "1",
        "extranet_root_privilege": "ALL PRIVILEGES ON *.*\nPROXY ON \"@\"",
        "mysql_root_init_password": "@123qwerTYUIOP",
        "mysql_base_path": mysql_dir + "base/" + version,
        "mysql_data_path": mysql_dir + "data/" + port,
        "mysql_binlog_path": mysql_dir + "log/binlog/" + port,
        "mysql_relaylog_path": mysql_dir + "log/relaylog/" + port,
        "mysql_redolog_path": mysql_dir + "log/redolog/" + port,
        "mysql_tmp_path": mysql_dir + "tmp/" + port,
        "backup_path": mysql_dir + "backup/" + port,
        "mycnf_path": mysql_dir + "etc/" + port + "/my.cnf",
        "version": version,
        "user_type": "single_user",
        "all_user": "universe_op",
        "all_host": "%",
        "all_password": "bupYE@-00",
        "all_privilege":
        "lock tables, process, reload, replication client, super, usage on *.*\nreplication slave, replication client on *.*\nshow databases, show view, update, super, create temporary tables, trigger, create view, alter routine, create routine, execute, file, create tablespace, create user, create, drop, grant option, lock tables, references, event, alter, delete, index, insert, select, usage on *.*\ncreate,select,insert,update,delete on universe.*\nselect on universe.*\nsuper on *.*\nsuper on *.*\nprocess on *.*\nreload on *.*\nreplication client on *.*\nsuper on *.*\nselect on performance_schema.*\nselect on mysql.*\nselect, execute on sys.*\nprocess on *.*\nevent on *.*\n",
        "run_user": "actiontech-mysql",
        "run_user_group": "",
        "mysql_uid": "",
        "mysql_gid": "",
        "mycnf_server_id": str(randint(1, 4294967295)),
        "umask": "0640",
        "umask_dir": "0750",
        "mycnf_config": mycnf
    }

    mycnf = api_post(context, "database/apply_my_cnf", install_params)
    install_params["mycnf_config"] = mycnf
    install_params["is_sync"] = True
    install_params["tag_list"] = "[]"

    api_request_post(context, "database/add_instance", install_params)


def get_mysql_installation_file(context):
    return get_installation_file(context, "mysql")


@then(
    u'the MySQL group should have {expect_count:int} running MySQL instance in {duration:time}'
)
def step_impl(context, expect_count, duration):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
        "group_id": context.mysql_group["group_id"],
    })
    data = resp["data"]
    assert len(data) == expect_count

    for i in range(1, duration * context.time_weight * 10):
        resp = api_get(context, "database/list_instance", {
            "group_id": context.mysql_group["group_id"],
        })
        condition = '.data[] | select(."mysql_status" != "STATUS_MYSQL_HEALTH_OK" or ."replication_status" != "STATUS_MYSQL_REPL_OK")'
        match = pyjq.first(condition, resp)
        if match == None:
            return
        time.sleep(0.1)
    assert False


@when(u'I found a MySQL master in the MySQL group')
def step_impl(context):
    assert context.mysql_group != None
    match = get_mysql_master_in_group(context, context.mysql_group["group_id"])
    assert match != None
    context.mysql_instance = match


def get_mysql_master_in_group(context, group_id):
    resp = api_get(context, "database/list_instance", {
        "group_id": group_id,
    })
    match = pyjq.first('.data[] | select(."role" == "STATUS_MYSQL_MASTER")',
                       resp)
    return match


@when(u'I make a manual backup on the MySQL instance')
def step_impl(context):
    assert context.mysql_instance != None
    resp = api_get(context, "urman_backupset/list", {
        "instance": context.mysql_instance["mysql_id"],
    })
    origin_id = pyjq.first('.data[] | .backup_set_id', resp)
    context.origin_id = origin_id
    cnf = api_get(context, "support/read_umc_file", {
        "path": "backupcnfs/backup.xtrabackup",
    })

    api_post(
        context, "database/manual_backup", {
            "is_sync": True,
            "mysql_id": context.mysql_instance["mysql_id"],
            "backup_tool": "Xtrabackup",
            "backup_cnf": cnf,
        })


@when(u'I add MySQL slave in the MySQL group')
def step_impl(context):
    assert context.mysql_group != None

    mysql_group_id = context.mysql_group["group_id"]
    mysql_master = get_mysql_master_in_group(context, mysql_group_id)

    context.execute_steps(u"""
			When I found a server with components ustats,udeploy,uguard-agent,urman-agent, except {server}
		""".format(server=mysql_master["server_id"]))

    resp = api_get(context, "support/init_data", {
        "group_id": mysql_group_id,
    })
    assert len(resp) > 0
    init_data = resp[-1]["name"]

    mysql_id = "mysql-" + generate_id()
    port = mysql_master["port"]
    install_file = get_mysql_installation_file(context)
    version = re.match(r".*(\d+\.\d+\.\d+).*", install_file).group(1)
    main_version = re.match(r"(\d+\.\d+)\.\d+", version).group(1)

    mycnf = mysql_master["mycnf"]

    install_params = {
        "server_id": context.server["server_id"],
        "group_id": context.mysql_group["group_id"],
        "port": port,
        "mysql_id": mysql_id,
        "mysql_alias": mysql_id,
        "mysql_tarball_path": install_file,
        "install_standard": "uguard_semi_sync",
        "init_data": init_data,
        "extranet_root_privilege": "",
        "mysql_base_path": mysql_master["mysql_base_path"],
        "mysql_data_path": mysql_master["mysql_data_path"],
        "mysql_binlog_path": mysql_master["mysql_binlog_path"],
        "mysql_relaylog_path": mysql_master["mysql_relaylog_path"],
        "mysql_redolog_path": mysql_master["mysql_redolog_path"],
        "mysql_tmp_path": mysql_master["mysql_tmp_path"],
        "backup_path": mysql_master["backup_path"],
        "mycnf_path": mysql_master["mycnf_path"],
        "version": version,
        "user_type": "single_user",
        "run_user": "actiontech-mysql",
        "run_user_group": "",
        "mysql_uid": "",
        "mysql_gid": "",
        "mycnf_server_id": str(randint(1, 4294967295)),
        "umask": "0640",
        "umask_dir": "0750",
        "mycnf_config": mycnf
    }

    mycnf = api_post(context, "database/apply_my_cnf", install_params)
    install_params["mycnf_config"] = mycnf
    install_params["is_sync"] = True
    install_params["tag_list"] = "[]"

    api_request_post(context, "database/add_instance", install_params)


@when(u'I enable HA on all MySQL instance in the MySQL group')
def step_impl(context):
    assert context.mysql_group != None

    mysql_group_id = context.mysql_group["group_id"]
    resp = api_get(context, "database/list_instance", {
        "group_id": mysql_group_id,
    })

    for inst in resp["data"]:
        api_post(
            context, "database/start_mysql_ha_enable", {
                "is_sync": True,
                "group_id": mysql_group_id,
                "mysql_id": inst["mysql_id"],
            })


@then(
    u'the MySQL group should have {master_count:int} running MySQL master and {slave_count:int} running MySQL slave in {duration:time}'
)
def step_impl(context, master_count, slave_count, duration):
    assert context.mysql_group != None

    for i in range(1, duration * context.time_weight * 10):
        resp = api_get(context, "database/list_instance", {
            "group_id": context.mysql_group["group_id"],
        })
        condition = '.data[] | select(."mysql_status" == "STATUS_MYSQL_HEALTH_OK" and ."replication_status" == "STATUS_MYSQL_REPL_OK")'
        masters = pyjq.all(
            condition + ' | select(."role" == "STATUS_MYSQL_MASTER")', resp)
        slaves = pyjq.all(
            condition + ' | select(."role" == "STATUS_MYSQL_SLAVE")', resp)
        if len(masters) == 1 and len(slaves) == 1:
            return
        time.sleep(0.1)
    assert False


@when(u'I remove MySQL instance')
def step_impl(context):
    assert context.mysql_instance != None

    body = {
        "mysql_id": context.mysql_instance['mysql_id'],
        "server_id": context.mysql_instance['server_id'],
        "group_id": context.mysql_instance['group_id'],
        "force": "0"
    }
    api_request_post(context, "database/delete_instance", body)


@then(
    u'the MySQL instance list should not contains the MySQL instance in {duration:time}'
)
def step_impl(context, duration):
    assert context.mysql_instance != None
    mysql_id = context.mysql_instance["mysql_id"]

    def condition(context, flag):
        resp = api_get(context, "database/list_instance",
                       {"number": context.page_size_to_select_all})
        match = pyjq.first('.data | any(."mysql_id" == "{0}")'.format(mysql_id),
                           resp)
        if match is not True:
            return True

    waitfor(context, condition, duration)


@when(u'I start MySQL instance ha enable')
def step_impl(context):
    assert context.mysql_instance != None
    body = {
        "server_id": context.mysql_instance['server_id'],
        "group_id": context.mysql_instance['group_id'],
        "mysql_id": context.mysql_instance['mysql_id'],
    }
    api_request_post(context, "database/start_mysql_ha_enable", body)


@then(u'MySQL instance ha enable should started in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_instance != None

    def condition(context, flag):
        mysql_id = context.mysql_instance["mysql_id"]
        resp = api_get(context, "database/list_instance", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(."mysql_id" == "{0}")'.format(mysql_id), resp)
        if match is not None and match['uguard_status'] == "UGUARD_ENABLE":
            return True

    waitfor(context, condition, duration)


@when(u'I configure MySQL group SIP')
def step_imp(context):
    assert context.mysql_group != None
    assert context.valid_sip != None
    body = {
        "group_id": context.mysql_group[0]['group_id'],
        "sip": context.valid_sip
    }
    api_request_post(context, "database/update_mysql_sip", body)


@then(u'update MySQL group SIP successful in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_group != None
    assert context.valid_sip != None
    mysql_group_id = context.mysql_group[0]["group_id"]

    def condition(context, flag):
        resp = api_get(context, "database/list_group", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.group_id == "{0}")'.format(mysql_group_id), resp)
        if "sip" not in match:
            return
        if match is not None and context.valid_sip == match['sip']:
            return True

    waitfor(context, condition, duration)


@when(u'I stop MySQL instance ha enable')
def step_impl(context):
    assert context.mysql_instance != None
    body = {
        "server_id": context.mysql_instance['server_id'],
        "group_id": context.mysql_instance['group_id'],
        "mysql_id": context.mysql_instance['mysql_id'],
        "is_sync": "true",
    }
    api_request_post(context, "database/stop_mysql_ha_enable", body)


@then(u'MySQL instance ha enable should stopped in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_instance != None

    def condition(context, flag):
        mysql_id = context.mysql_instance["mysql_id"]
        resp = api_get(context, "database/list_instance", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(."mysql_id" == "{0}")'.format(mysql_id), resp)
        if match is not None and match['uguard_status'] == "MANUAL_EXCLUDE_HA":
            return True

    waitfor(context, condition, duration)


@when(u'I found a running MySQL instance and uguard enable,or I skip the test')
def step_impl(context):
    resp = api_get(context, "database/list_group", {
        "number": context.page_size_to_select_all,
    })
    match = pyjq.first('.data[] | select(.group_instance_num == "1")', resp)
    if match is None:
        context.scenario.skip("Found no MySQL instance")
        return
    mysqls = api_get(context, "database/list_instance", {
        "number": context.page_size_to_select_all,
    })
    mysql = pyjq.first(
        '.data[] | select(.mysql_status == "STATUS_MYSQL_HEALTH_OK" and .uguard_status == "UGUARD_ENABLE" and .group_id == "{0}" )'
        .format(match['group_id']), mysqls)
    if mysql is None:
        context.scenario.skip("Found no MySQL instance UGUARD_ENABLE")
        return
    else:
        root_password = api_get(context, "helper/get_mysql_password", {
            "mysql_id": mysql["mysql_id"],
            "password_type": "ROOT",
        })
        mysql["root_password"] = root_password
        context.mysql_instance = mysql


@when(u'I stop MySQL service')
def step_imp(context):
    assert context.mysql_instance != None
    body = {
        "server_id": context.mysql_instance['server_id'],
        "mysql_id": context.mysql_instance['mysql_id'],
        "is_sync": "true",
    }
    api_request_post(context, "database/stop_mysql_service", body)


@then(u'stop MySQL service should succeed in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_instance != None

    def condition(context, flag):
        resp = api_get(context, "database/list_instance", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.mysql_status == "STATUS_MYSQL_HEALTH_BAD")',
            resp)
        if match is not None:
            return True

    waitfor(context, condition, duration)


@when(u'I reset database instance')
def step_imp(context):
    assert context.mysql_instance != None
    resp = api_get(context, "support/init_data", {
        "group_id": context.mysql_instance['group_id'],
    })
    assert len(resp) > 0
    init_data = resp[-1]["name"]
    body = {
        "server_id": context.mysql_instance['server_id'],
        "mysql_id": context.mysql_instance['mysql_id'],
        "origin_data": init_data
    }
    api_request_post(context, "database/reset_database_instance", body)


@then(u'reset database instance should succeed in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_instance != None

    def condition(context, flag):
        resp = api_get(context, "database/list_instance", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.mysql_status == "STATUS_MYSQL_HEALTH_OK" '
            'and ."mysql_id" == "{0}")'.format(
                context.mysql_instance['mysql_id']), resp)
        if match is not None:
            return True

    waitfor(context, condition, duration)


@when(
    u'I found {count:int} MySQL group{s:s?} with MySQL HA instances, or I skip the test'
)
def step_imp(context, count, s):
    res = api_get(context, "database/list_group", {
        "number": context.page_size_to_select_all,
    })
    matches = pyjq.all(
        '.data[] | select(.uguard_status == "UGUARD_PRIMARY_SLAVE_ENABLE")',
        res)
    if matches is None:
        context.scenario.skip("Found no MySQL group with MySQL HA instance")
        return
    if len(matches) < count:
        context.scenario.skip(
            "Found no enough MySQL groups with MySQL HA instance")
        return
    if count == 1:
        context.mysql_group = matches
    else:
        context.mysql_groups = matches[:count]


@when(u'I promote slave instance to master')
def step_imp(context):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
        "group_id": context.mysql_group[0]["group_id"],
    })
    the_slave = pyjq.first('.data[]|select(."role" == "STATUS_MYSQL_SLAVE")',
                           resp)
    body = {"mysql_id": the_slave['mysql_id']}
    api_request_post(context, "database/promote_to_master", body)
    context.slave_instance = the_slave


@then(u'promote slave instance to master should succeed in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_group != None

    def condition(context, flag):
        resp = api_get(context, "database/list_instance", {
            "group_id": context.mysql_group[0]["group_id"],
        })
        condition = '.data[] | select(."mysql_status" == "STATUS_MYSQL_HEALTH_OK" and ."replication_status" == "STATUS_MYSQL_REPL_OK" and ."sip" == "(SIP)")'
        masters = pyjq.all(
            condition +
            ' | select(."role" == "STATUS_MYSQL_MASTER" and ."mysql_id" =="{0}")'
            .format(context.slave_instance['mysql_id']), resp)

        if len(masters) == 1:
            return True

    waitfor(context, condition, duration)


def get_mysql_instance_root_password(context, inst_id):
    root_password = api_get(context, "helper/get_mysql_password", {
        "mysql_id": inst_id,
        "password_type": "ROOT",
    })
    return root_password


@when(u'I query the slave instance "{query}"')
def step_impl(context, query):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
        "group_id": context.mysql_group[0]["group_id"],
    })
    the_slave = pyjq.first('.data[]|select(."role" == "STATUS_MYSQL_SLAVE")',
                           resp)
    master = pyjq.first('.data[]|select(."role" == "STATUS_MYSQL_MASTER")',
                        resp)

    master["root_password"] = get_mysql_instance_root_password(
        context, master["mysql_id"])

    resp = api_get(
        context, "helper/query_mysql", {
            "mysql_id": the_slave["mysql_id"],
            "query": query,
            "user": "root",
            "password": master["root_password"],
        })
    context.mysql_resp = resp


@when(u'I execute the MySQL instance "{option}"')
def step_impl(context, option):
    assert context.mysql_instance != None
    mysql = context.mysql_instance

    resp = api_get(
        context, "helper/query_mysql", {
            "mysql_id": mysql["mysql_id"],
            "query": option,
            "user": "root",
            "password": mysql["root_password"],
        })


@when(u'I add sla protocol')
def step_imp(context):
    assert context.mysql_instance != None
    body = {
        "group_id": context.mysql_instance['group_id'],
        "add_sla_template": "SLA_RPO_sample",
        "is_sync": "true",
    }
    api_request_post(context, "/database/add_sla_protocol", body)


@then(u'sla protocol should add succeed in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_instance != None

    def condition(context, flag):
        res = api_get(context, "database/list_group", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.group_id == "{0}")'.format(
                context.mysql_instance["group_id"]), res)

        if match is not None and match['sla_template'] == "SLA_RPO_sample":
            return True

    waitfor(context, condition, duration)


@when(u'I start sla protocol')
def step_imp(context):
    assert context.mysql_instance != None
    api_request_post(context, "/database/start_sla_protocol", {
        "group_id": context.mysql_instance['group_id'],
        "is_sync": "true",
    })


@then(u'sla protocol should started')
def step_imp(context):
    assert context.mysql_instance != None
    res = api_get(context, "database/list_group", {
        "number": context.page_size_to_select_all,
    })
    match = pyjq.first(
        '.data[] | select(.group_id == "{0}")'.format(
            context.mysql_instance["group_id"]), res)
    if match['sla_enable'] == "ENABLE":
        return
    assert False


def get_mysql_group_brief(context, group_id):
    resp = api_get(context, "database/list_instance", {"group_id": group_id})
    master = pyjq.first('.data[] | select(.role == "STATUS_MYSQL_MASTER")',
                        resp)
    assert master is not None
    root_password = get_mysql_instance_root_password(context,
                                                     master["mysql_id"])
    slave = pyjq.first('.data[] | select(.role == "STATUS_MYSQL_SLAVE")', resp)
    assert slave is not None

    return {
        "group_id": group_id,
        "master_id": master["mysql_id"],
        "master_addr": master["server_addr"] + ":" + master["port"],
        "slave_id": slave["mysql_id"],
        "slave_addr": slave["server_addr"] + ":" + slave["port"],
        "root_password": root_password
    }


@when(u'I kill three master pid')
def step_imp(context):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
        "group_id": context.mysql_group[0]["group_id"],
    })
    master = pyjq.first('.data[]|select(."role" == "STATUS_MYSQL_MASTER")',
                        resp)
    for i in range(1, 4):
        api_request_post(context, "/helper/kill_mysql_process", {
            "mysql_id": master['mysql_id'],
            "is_sync": "true",
        })
        time.sleep(5)

    context.master_info = master
    context.start_time = time.time()


@then(u"master-slave switching in {duration:time}")
def step_imp(context, duration):

    def condition(context, flag):
        resp = api_get(context, "database/list_instance", {
            "group_id": context.mysql_group[0]["group_id"],
        })
        master = pyjq.first(
            '.data[]|select(."role" == "STATUS_MYSQL_MASTER" and ."replication_status" == "STATUS_MYSQL_REPL_OK" and ."sip" == "(SIP)")',
            resp)
        if master is not None and master['mysql_id'] != context.master_info[
                'mysql_id']:
            return True

    waitfor(context, condition, duration)


@when(u'I found alert code {code:string}, or I skip the test')
def step_imp(context, code):
    resp = api_get(context, "/alert_record/list_search", {
        'order_by': 'timestamp',
        'ascending': 'false',
    })

    alert_info = pyjq.first('.data[]|select(."code" == {0})'.format(code), resp)
    if alert_info is not None:
        context.scenario.skip("Found alert code")
        return
    else:
        assert True


@then(u'expect alert code {code:string} in {duration:time}')
def step_imp(context, code, duration):

    def condition(context, flag):
        resp = api_get(context, "/alert_record/list_search", {
            'order_by': 'timestamp',
            'ascending': 'false',
        })

        alert_info = pyjq.first('.data[]|select(."code" == {0})'.format(code),
                                resp)
        if alert_info is not None and context.master_info[
                'server_id'] == alert_info['server']:
            return True

    waitfor(context, condition, duration)


@when(u'I create MySQL user "{user}" and grants "{grants}"')
def step_imp(context, user, grants):
    assert context.mysql_instance != None
    mysql = context.mysql_instance
    api_request_post(
        context, "database/create_mysql_user", {
            "group_id": mysql['group_id'],
            "admin_user": "root",
            "admin_password": mysql["root_password"],
            "mysql_connect_type": "socket",
            "master_instance": mysql['mysql_id'],
            "user": user,
            "user_host": "%",
            "password": "@123qwerTYUIOP",
            "grants": grants,
            "is_sync": "true",
        })


@when(u'I update MySQL user "{user}" and password "{password}"')
def step_imp(context, user, password):
    assert context.mysql_instance != None
    mysql = context.mysql_instance
    context.update_password = password
    api_request_post(
        context, "database/update_mysql_user_password", {
            "group_id": mysql['group_id'],
            "admin_user": "root",
            "admin_password": mysql["root_password"],
            "mysql_connect_type": "socket",
            "master_instance": mysql['mysql_id'],
            "user": user,
            "user_host": "%",
            "update_password": password,
            "is_sync": "true",
        })


@when(u'I query the MySQL instance use user "{user}" "{query:any}"')
def step_imp(context, query, user):
    assert context.mysql_instance != None
    mysql = context.mysql_instance
    password = context.update_password
    resp = api_get(
        context, "helper/query_mysql", {
            "mysql_id": mysql["mysql_id"],
            "query": query,
            "user": user,
            "password": password,
        })
    context.mysql_resp = resp


@when(u'I detach MySQL instance')
def step_imp(context):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
        "group_id": context.mysql_group[0]["group_id"],
    })
    slave_info = pyjq.first('.data[] | select(.role == "STATUS_MYSQL_SLAVE")',
                            resp)
    assert slave_info is not None
    context.mysql_instance = slave_info
    context.execute_steps(u"""
        When I stop MySQL instance ha enable
        Then the response is ok
        And MySQL instance ha enable should stopped in 2m
                          """)
    api_request_post(
        context, "database/detach_instance", {
            "mysql_id": context.mysql_instance['mysql_id'],
            "server_id": context.mysql_instance['server_id'],
            "group_id": context.mysql_instance['group_id'],
            "force": "1",
            "is_sync": "true",
        })


@then(u'the MySQL instance should be detached in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_group != None
    assert context.mysql_instance != None

    def condition(context, flag):
        resp = api_get(context, "database/list_instance", {
            "group_id": context.mysql_group[0]["group_id"],
        })
        match = pyjq.first(
            '.data | any(."mysql_id" == "{0}")'.format(
                context.mysql_instance['mysql_id']), resp)
        if match is not True:
            return True

    waitfor(context, condition, duration)


@when(u'I takeover MySQL instance')
def step_imp(context):
    assert context.mysql_group != None
    assert context.mysql_instance != None
    mysql_id = "mysql-" + generate_id()
    passwd = get_master_root_password(context)

    body = {
        "server_id": context.mysql_instance['server_id'],
        "group_id": context.mysql_instance['group_id'],
        "port": context.mysql_instance['port'],
        "mysql_id": mysql_id,
        "mysql_alias": mysql_id,
        "mysql_tarball_path": context.mysql_instance['mysql_tarball_path'],
        "install_standard": "uguard_semi_sync",
        "mysql_user": "root",
        "mysql_password": passwd,
        "mysql_connect_type": "socket",
        "mysql_socket_path":
        context.mysql_instance['mysql_data_path'] + "/mysqld.sock",
        "backup_path": context.mysql_instance['backup_path'],
        "mycnf_path": context.mysql_instance['mycnf_path'],
        "version": context.mysql_instance['version'],
        "user_type": "single_user",
        "run_user": context.mysql_instance['run_user'],
        "run_user_group": "",
        "mysql_uid": "",
        "mysql_gid": "",
        "umask": "0640",
        "umask_dir": "0750",
        "tag_list": "[]",
        "resource": "0"
    }
    api_request_post(context, "/database/takeover_instance", body)


def get_master_root_password(context):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
        "group_id": context.mysql_group[0]["group_id"],
    })
    master_info = pyjq.first('.data[] | select(.role == "STATUS_MYSQL_MASTER")',
                             resp)
    assert master_info is not None
    root_password = api_get(context, "helper/get_mysql_password", {
        "mysql_id": master_info["mysql_id"],
        "password_type": "ROOT",
    })
    return root_password


@then(u'takeover MySQL instance should succeed in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_group != None

    def condition(context, flag):
        res = api_get(context, "database/list_group", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.group_instance_num == "2" and ."group_id" == "{0}")'
            .format(context.mysql_instance["group_id"]), res)
        if match is not None:
            resp = api_get(context, "database/list_instance", {
                "group_id": context.mysql_instance["group_id"],
            })
            res = pyjq.first(
                '.data|any(."mysql_status" == "STATUS_MYSQL_HEALTH_BAD")', resp)
            if res is not True:
                return True

    waitfor(context, condition, duration)


@when(u'I exclude ha MySQL instance')
def step_imp(context):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
        "group_id": context.mysql_group[0]["group_id"],
    })
    slave = pyjq.first('.data[] | select(.role == "STATUS_MYSQL_SLAVE")', resp)
    assert slave is not None
    context.mysql_instance = slave
    context.execute_steps(u"""
    When I stop MySQL instance ha enable
    """)


@when(u'I add sla protocol "{sla}"')
def step_imp(context, sla):
    assert context.mysql_group != None
    body = {
        "group_id": context.mysql_group[0]["group_id"],
        "add_sla_template": sla,
        "is_sync": "true",
    }
    api_request_post(context, "/database/add_sla_protocol", body)


@then(u'sla protocol "{sla}" should add succeed in {duration:time}')
def step_imp(context, duration, sla):
    assert context.mysql_group != None

    def condition(context, flag):
        res = api_get(context, "database/list_group", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.group_id == "{0}")'.format(
                context.mysql_group[0]["group_id"]), res)

        if match is not None and match['sla_template'] == sla:
            return True

    waitfor(context, condition, duration)


@when(u'I start the group SLA protocol')
def step_imp(context):
    assert context.mysql_group != None
    api_request_post(context, "/database/start_sla_protocol", {
        "group_id": context.mysql_group[0]["group_id"],
        "is_sync": "true",
    })


@then(u'the group SLA protocol should started')
def step_imp(context):
    assert context.mysql_group != None
    res = api_get(context, "database/list_group", {
        "number": context.page_size_to_select_all,
    })
    match = pyjq.first(
        '.data[] | select(.group_id == "{0}")'.format(
            context.mysql_group[0]["group_id"]), res)
    if match['sla_enable'] == "ENABLE":
        return
    assert False


@then(
    u'expect alert code {code:string} and detail "{detail}" in {duration:time}')
def step_imp(context, code, detail, duration):

    def condition(context, flag):
        resp = api_get(context, "/alert_record/list_search", {
            'order_by': 'timestamp',
            'ascending': 'false',
        })
        alert_info = pyjq.first('.data[]|select(."code" == {0})'.format(code),
                                resp)
        if alert_info is not None and detail in alert_info['detail']:
            return True

    waitfor(context, condition, duration)


@then(u'group sla level {level:string} in {duration:time}')
def step_imp(context, level, duration):
    assert context.mysql_group != None

    def condition(context, flag):
        res = api_get(context, "database/list_group", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.group_id == "{0}")'.format(
                context.mysql_group[0]["group_id"]), res)
        if match is not None and "sla_level" not in match:
            return
        if match['sla_level'] == level:
            return True

    waitfor(context, condition, duration)


@when(u'I remove the group SLA protocol')
def step_imp(context):
    assert context.mysql_group != None
    body = {
        "group_id": context.mysql_group[0]["group_id"],
        "is_sync": "true",
    }
    api_request_post(context, "/database/remove_sla_protocol", body)


@when(u'I pause the group SLA protocol')
def step_imp(context):
    assert context.mysql_group != None
    body = {
        "group_id": context.mysql_group[0]["group_id"],
        "is_sync": "true",
    }
    api_request_post(context, "/database/pause_sla_protocol", body)


@then(u'the group SLA protocol should paused in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_group != None

    def condition(context, flag):
        res = api_get(context, "database/list_group", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.group_id == "{0}")'.format(
                context.mysql_group[0]["group_id"]), res)
        assert match is not None
        if match['sla_enable'] == "DISABLE":
            return True

    waitfor(context, condition, duration)


@then(u'the group SLA protocol should remove succeed in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_group != None

    def condition(context, flag):
        res = api_get(context, "database/list_group", {
            "number": context.page_size_to_select_all,
        })
        match = pyjq.first(
            '.data[] | select(.group_id == "{0}")'.format(
                context.mysql_group[0]["group_id"]), res)
        if match is not None and 'sla_template' not in match:
            return True

    waitfor(context, condition, duration)

@when(u'I add the ip "{ip}" to sip pool')
def step_imp(context, ip):
    sip = ip
    api_request_post(context, "sippool/add", {
        "sip": sip,
        "is_sync": "true",
    })


@when(u'I action {action:string} MySQL instance component {component:string}')
def step_imp(context, action, component):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
        "group_id": context.mysql_group[0]["group_id"],
    })
    slave = pyjq.first('.data[] | select(.role == "STATUS_MYSQL_SLAVE")', resp)
    assert slave is not None
    context.mysql_instance = slave
    if action.lower() == "pause":
        context.execute_steps(u"""
        When I pause component {0}
            """.format(component))
    else:
        context.execute_steps(u"""
    	When I start component {0}
    	    """.format(component))


@when(u'I pause component {component:string}')
def step_imp(context, component):
    assert context.mysql_instance != None
    api_request_post(context, "/server/pause", {
        "server_id": context.mysql_instance['server_id'],
        "component": component,
        "is_sync": "true",
    })


@when(u'I start component {component:string}')
def step_imp(context, component):
    assert context.mysql_instance != None
    api_request_post(context, "/server/start", {
        "server_id": context.mysql_instance['server_id'],
        "component": component,
        "is_sync": "true",
    })

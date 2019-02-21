from behave import *
from framework.api import *
import pyjq
import time
import json
import re
from util import *

use_step_matcher("cfparse")

@when(u'I found a running MySQL instance, or I skip the test')
def step_impl(context):
	mysqls = api_get(context, "database/list_instance", {
		"number": context.page_size_to_select_all,
	})
	mysql = pyjq.first('.data[] | select(.mysql_status == "STATUS_MYSQL_HEALTH_OK")', mysqls)
	if mysql is None:
		context.scenario.skip("Found no MySQL instance without backup rule")
		return

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

	resp = api_get(context, "helper/query_mysql", {
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


@then(u'the MySQL group list {should_or_not:should_or_not} contains the MySQL group')
def step_impl(context, should_or_not):
	assert context.mysql_group != None
	mysql_group_id = context.mysql_group["group_id"]

	resp = api_get(context, "database/list_group", {
		"number": context.page_size_to_select_all,
	})
	match = pyjq.first('.data[] | select(.group_id == "{0}")'.format(mysql_group_id), resp)
	assert (match != None and should_or_not) or (match == None and not should_or_not)

@when(u'I found a MySQL group without MySQL instance, and without SIP, or I skip the test')
def step_impl(context):
	resp = api_get(context, "database/list_group", {
		"number": context.page_size_to_select_all,
	})
	match = pyjq.first('.data[] | select(.group_instance_num == "0") | select(has("sip") | not)', resp)
	if match is None:
		context.scenario.skip("Found no MySQL group without MySQL instance, and without SIP")
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

	mycnf = mycnf.replace("innodb_data_file_path = ibdata1:1G:autoextend", "innodb_data_file_path = ibdata1:64M:autoextend")

	install_params = {
		"server_id": context.server["server_id"],
        "group_id": context.mysql_group["group_id"],
        "port": port,
        "mysql_id": mysql_id,
        "mysql_alias": mysql_id,
        "mysql_tarball_path": install_file,
        "install_standard": "uguard_semi_sync",
        "init_data": "",
		"create_extranet_root":"1",
		"extranet_root_privilege":"ALL PRIVILEGES ON *.*\nPROXY ON \"@\"",
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
        "all_privilege": "lock tables, process, reload, replication client, super, usage on *.*\nreplication slave, replication client on *.*\nshow databases, show view, update, super, create temporary tables, trigger, create view, alter routine, create routine, execute, file, create tablespace, create user, create, drop, grant option, lock tables, references, event, alter, delete, index, insert, select, usage on *.*\ncreate,select,insert,update,delete on universe.*\nselect on universe.*\nsuper on *.*\nsuper on *.*\nprocess on *.*\nreload on *.*\nreplication client on *.*\nsuper on *.*\nselect on performance_schema.*\nselect on mysql.*\nselect, execute on sys.*\nprocess on *.*\nevent on *.*\n",
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
	resp = api_get(context, "support/component", {
		"pattern": "mysql",
	})
	assert len(resp) > 0
	return resp[-1]["Name"]


@then(u'the MySQL group should have {expect_count:int} running MySQL instance in {duration:time}')
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
	match = pyjq.first('.data[] | select(."role" == "STATUS_MYSQL_MASTER")', resp)
	return match

@when(u'I make a manual backup on the MySQL instance')
def step_impl(context):
	assert context.mysql_instance != None
	cnf = api_get(context, "support/read_umc_file", {
		"path": "backupcnfs/backup.xtrabackup", 
	})

	api_post(context, "database/manual_backup", {
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
		api_post(context, "database/start_mysql_ha_enable", {
			"is_sync": True,
			"group_id": mysql_group_id,
			"mysql_id": inst["mysql_id"],
		})

@then(u'the MySQL group should have {master_count:int} running MySQL master and {slave_count:int} running MySQL slave in {duration:time}')
def step_impl(context, master_count, slave_count, duration):
	assert context.mysql_group != None

	for i in range(1, duration * context.time_weight * 10):
		resp = api_get(context, "database/list_instance", {
			"group_id": context.mysql_group["group_id"],
		})
		condition = '.data[] | select(."mysql_status" == "STATUS_MYSQL_HEALTH_OK" and ."replication_status" == "STATUS_MYSQL_REPL_OK")'
		masters = pyjq.all(condition + ' | select(."role" == "STATUS_MYSQL_MASTER")', resp)
		slaves = pyjq.all(condition + ' | select(."role" == "STATUS_MYSQL_SLAVE")', resp)
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


@then(u'the MySQL instance list should not contains the MySQL instance in {duration:time}')
def step_impl(context, duration):
    assert context.mysql_instance != None
    mysql_id = context.mysql_instance["mysql_id"]
    def condition(context, flag):
        resp = api_get(context, "database/list_instance", {
            "number": context.page_size_to_select_all})
        match = pyjq.first('.data | any(."mysql_id" == "{0}")'.format(mysql_id), resp)
        if match is not True:
            return True
    waitfor(context, condition, duration)


@when(u'start MySQL instance ha enable')
def step_impl(context):
	assert context.mysql_instance != None
	body = {
		"server_id": context.mysql_instance['server_id'],
		"group_id": context.mysql_instance['group_id'],
		"mysql_id": context.mysql_instance['mysql_id']
	}
	api_request_post(context, "database/start_mysql_ha_enable", body)

@then(u'MySQL instance ha enable should started')
def step_imp(context):
	assert context.mysql_instance != None
	mysql_id = context.mysql_instance["mysql_id"]
	resp = api_get(context, "database/list_instance", {
		"number": context.page_size_to_select_all,
	})
	match = pyjq.first('.data[] | select(."mysql_id" == "{0}")'.format(mysql_id), resp)
	if match['uguard_status'] == "UGUARD_ENABLE":
		return
	assert False


@when(u'I configure MySQL group SIP')
def step_imp(context):
    assert context.mysql_group != None
    assert context.valid_sip != None
    body = {
        "group_id": context.mysql_group['group_id'],
        "sip": context.valid_sip
    }
    api_request_post(context, "database/update_mysql_sip", body)

@then(u'update MySQL group SIP successful in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_group != None
    assert context.valid_sip != None
    mysql_group_id = context.mysql_group["group_id"]
    def condition(context, flag):
        resp = api_get(context, "database/list_group", {
			"number": context.page_size_to_select_all,
		})
        match = pyjq.first('.data[] | select(.group_id == "{0}")'.format(mysql_group_id), resp)
        if context.valid_sip == match['sip']:
            return True
    waitfor(context, condition, duration)

@when(u'stop MySQL instance ha enable')
def step_impl(context):
	assert context.mysql_instance != None
	body = {
		"server_id": context.mysql_instance['server_id'],
		"group_id": context.mysql_instance['group_id'],
		"mysql_id": context.mysql_instance['mysql_id']
	}
	api_request_post(context, "database/stop_mysql_ha_enable", body)

@then(u'MySQL instance ha enable should stopped')
def step_imp(context):
	assert context.mysql_instance != None
	mysql_id = context.mysql_instance["mysql_id"]
	resp = api_get(context, "database/list_instance", {
		"number": context.page_size_to_select_all,
	})
	match = pyjq.first('.data[] | select(."mysql_id" == "{0}")'.format(mysql_id), resp)
	if match['uguard_status'] == "MANUAL_EXCLUDE_HA":
		return
	assert False

@when(u'I found a running MySQL instance and uguard enable,or I skip the test')
def step_impl(context):
	mysqls = api_get(context, "database/list_instance", {
		"number": context.page_size_to_select_all,
	})
	mysql = pyjq.first('.data[] | select(."mysql_status" == "STATUS_MYSQL_HEALTH_OK" and ."uguard_status" == "UGUARD_ENABLE")', mysqls)
	if mysql is None:
		context.scenario.skip("Found no MySQL instance UGUARD_ENABLE")
		return

	root_password = api_get(context, "helper/get_mysql_password", {
		"mysql_id": mysql["mysql_id"],
		"password_type": "ROOT",
	})
	mysql["root_password"] = root_password
	context.mysql_instance = mysql

@when(u'stop MySQL service')
def step_imp(context):
    assert context.mysql_instance != None
    body = {
		"server_id": context.mysql_instance['server_id'],
		"mysql_id": context.mysql_instance['mysql_id']
	}
    api_request_post(context, "database/stop_mysql_service", body)

@then(u'stop MySQL service should succeed in {duration:time}')
def step_imp(context,duration):
    assert context.mysql_instance !=None
    def condition(context, flag):
        resp = api_get(context, "database/list_instance", {
            "number": context.page_size_to_select_all,
		})
        match = pyjq.first('.data[] | select(.mysql_status == "STATUS_MYSQL_HEALTH_BAD")', resp)
        if match is not None:
            return True
    waitfor(context, condition, duration)

@when(u'reset database instance')
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
        match = pyjq.first('.data[] | select(.mysql_status == "STATUS_MYSQL_HEALTH_OK" '
						   'and ."mysql_id" == "{0}")'.format(context.mysql_instance['mysql_id']), resp)
        if match is not None:
            return True
    waitfor(context, condition, duration)

@when(u'I found one group high availability instance')
def step_imp(context):
    res = api_get(context, "database/list_group", {
		"number": context.page_size_to_select_all,
	})
    match = pyjq.first('.data[] | select(.group_instance_num > "1")', res)
    if match is None:
        context.scenario.skip("Found no MySQL group without MySQL high availability instance")
    else:
        context.mysql_group = match

    resp = api_get(context, "database/list_instance", {
		"group_id": context.mysql_group["group_id"],
	})
    condition = '.data[] | select(."mysql_status" == "STATUS_MYSQL_HEALTH_OK" and ."replication_status" == "STATUS_MYSQL_REPL_OK")'
    masters = pyjq.all(condition + ' | select(."role" == "STATUS_MYSQL_MASTER")', resp)
    slaves = pyjq.all(condition + ' | select(."role" == "STATUS_MYSQL_SLAVE")', resp)
    if len(masters) == 1 and len(slaves) > 0:
        return
    assert False

@when(u'promote slave instance to master')
def step_imp(context):
    assert context.mysql_group != None
    resp = api_get(context, "database/list_instance", {
		"group_id": context.mysql_group["group_id"],
	})
    the_slave = pyjq.first('.data[]|select(."role" == "STATUS_MYSQL_SLAVE")', resp)
    body = {"mysql_id":the_slave['mysql_id']}
    api_request_post(context, "database/promote_to_master", body)
    context.slave_instance = the_slave

@then(u'promote slave instance to master should succeed in {duration:time}')
def step_imp(context, duration):
    assert context.mysql_group != None

    def condition(context, flag):
        resp = api_get(context, "database/list_instance", {
			"group_id": context.mysql_group["group_id"],
		})
        condition = '.data[] | select(."mysql_status" == "STATUS_MYSQL_HEALTH_OK" and ."replication_status" == "STATUS_MYSQL_REPL_OK" and ."sip" == "(SIP)")'
        masters = pyjq.all(condition + ' | select(."role" == "STATUS_MYSQL_MASTER" and ."mysql_id" =="{0}")'.format(context.slave_instance['mysql_id']), resp)

        if len(masters) == 1:
            return True
    waitfor(context, condition, duration)

@when(u'I query the slave instance "{query}"')
def step_impl(context, query):
	assert context.mysql_group != None
	resp = api_get(context, "database/list_instance", {
		"group_id": context.mysql_group["group_id"],
	})
	the_slave = pyjq.first('.data[]|select(."role" == "STATUS_MYSQL_SLAVE")', resp)
	master = pyjq.first('.data[]|select(."role" == "STATUS_MYSQL_MASTER")', resp)

	root_password = api_get(context, "helper/get_mysql_password", {
		"mysql_id": master["mysql_id"],
		"password_type": "ROOT",
	})
	master["root_password"] = root_password

	resp = api_get(context, "helper/query_mysql", {
		"mysql_id": the_slave["mysql_id"],
		"query": query,
		"user": "root",
		"password": master["root_password"],
	})
	context.mysql_resp = resp


@when(u'I execution action the MySQL instance "{option}"')
def step_impl(context, option):
	assert context.mysql_instance != None
	mysql = context.mysql_instance

	resp = api_get(context, "helper/query_mysql", {
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
		match = pyjq.first('.data[] | select(.group_id == "{0}")'.format(context.mysql_instance["group_id"]), res)
		print ("output result:")
		print (match)
		if match['sla_template'] == "SLA_RPO_sample":
			return True
	waitfor(context, condition, duration)

@when(u'I start sla protocol')
def step_imp(context):
	assert context.mysql_instance != None
	api_request_post(context, "/database/start_sla_protocol",{
		"group_id": context.mysql_instance['group_id'],
		"is_sync": "true",
	})

@then(u'sla protocol should started')
def step_imp(context):
	assert context.mysql_instance != None
	res = api_get(context, "database/list_group", {
		"number": context.page_size_to_select_all,
	})
	match = pyjq.first('.data[] | select(.group_id == "{0}")'.format(context.mysql_instance["group_id"]), res)
	if match['sla_enable'] == "ENABLE":
		return
	assert False


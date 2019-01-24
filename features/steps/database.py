from behave import *
from framework.api import *
import pyjq
import time
import json
import random
import re

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

	mysql_group_id = "mysql-group-" + str(int(time.time()))

	api_request_post(context, "database/add_group", {
		"is_sync": True,
		"group_id": mysql_group_id,
		"sip": sip,
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

@when(u'I found a valid MySQL port, or I skip the test')
def step_impl(context):
	for _ in range(1,1024):
		port = random.randint(6000, 65535)
		resp = api_get(context, "database/list_instance", {
			"port": str(port),
		})
		if len(resp["data"]) == 0:
			context.valid_port = str(port)
			return

	context.scenario.skip("Found no valid MySQL port")

@when(u'I add MySQL instance in the MySQL group')
def step_impl(context):
	assert context.mysql_group != None
	assert context.valid_port != None
	assert context.server != None
	mysql_group_id = context.mysql_group["group_id"]
	mysql_id = "mysql-" + str(int(time.time()))
	mysql_dir = context.mysql_installation_dir
	port = context.valid_port
	install_file = get_mysql_installation_file(context)
	version = re.match(r".*(\d+\.\d+\.\d+).*", install_file).group(1)
	main_version = re.match(r"(\d+\.\d+)\.\d+", version).group(1)

	mycnf = api_get(context, "support/read_umc_file", {
		"path": "mycnfs/my.cnf." + main_version, 
	})

	install_params = {
		"server_id": context.server["server_id"],
        "group_id": context.mysql_group["group_id"],
        "port": context.valid_port,
        "mysql_id": mysql_id,
        "mysql_alias": mysql_id,
        "mysql_tarball_path": install_file,
        "install_standard": "uguard_semi_sync",
        "init_data": "",
        "extranet_root_privilege": "",
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
        "mycnf_server_id": str(random.randint(1, 99999999999)),
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
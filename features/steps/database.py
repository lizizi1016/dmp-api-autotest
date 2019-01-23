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
	print("version")
	print(version)
	main_version = re.match(r"(\d+\.\d+)\.\d+", version).group(1)

#TODO use readfile("./mycnfs/my.cnf." + main_version) to read mycnf
	mycnf = """
[mysqld]

# DO NOT MODIFY, Universe will generate this part
port = 3306
server_id = 123456
basedir = /opt/mysql/base
datadir = /opt/mysql/data/3306
log_bin = /opt/mysql/binlog/3306
tmpdir = /opt/mysql/tmp/3306
relay_log = /opt/mysql/relaylog/3306
innodb_log_group_home_dir = /opt/mysql/innodblog/3306
log_error = mysql-error.log
report_host = 127.0.0.1

# BINLOG
binlog_error_action = ABORT_SERVER
binlog_format = row
binlog_rows_query_log_events = 1
log_slave_updates = 1
master_info_repository = TABLE
max_binlog_size = 250M
relay_log_info_repository = TABLE
relay_log_recovery = 1
sync_binlog = 1

# GTID #
gtid_mode = ON
enforce_gtid_consistency = 1

# ENGINE
default_storage_engine = InnoDB
innodb_buffer_pool_size = 128M
innodb_data_file_path = ibdata1:1G:autoextend
innodb_file_per_table = 1
innodb_flush_log_at_trx_commit=1
innodb_flush_method = O_DIRECT
innodb_io_capacity = 1000
innodb_log_buffer_size = 64M
innodb_log_file_size = 2G
innodb_log_files_in_group = 2
innodb_max_dirty_pages_pct = 60
innodb_print_all_deadlocks=1
innodb_stats_on_metadata = 0
innodb_strict_mode = 1
#innodb_undo_logs=128 #Deprecated In 5.7.19
#innodb_undo_tablespaces=3 #Deprecated In 5.7.21
innodb_max_undo_log_size=4G
innodb_undo_log_truncate=1
innodb_read_io_threads = 8
innodb_write_io_threads = 8
innodb_purge_threads = 8
innodb_buffer_pool_load_at_startup = 1
innodb_buffer_pool_dump_at_shutdown = 1
innodb_buffer_pool_dump_pct=25
innodb_sort_buffer_size = 8M
#innodb_page_cleaners = 8
#innodb_buffer_pool_instances = 8

# CACHE
key_buffer_size = 32M
tmp_table_size = 32M
max_heap_table_size = 32M
table_open_cache = 1024
query_cache_type = 0
query_cache_size = 0
max_connections = 2000
thread_cache_size = 1024
open_files_limit = 65535
binlog_cache_size = 1M
join_buffer_size = 8M
sort_buffer_size = 8M

# SLOW LOG
slow_query_log = 1
slow_query_log_file = mysql-slow.log
log_slow_admin_statements = 1
log_slow_slave_statements = 1
long_query_time  = 1

# SEMISYNC #
plugin_load = "rpl_semi_sync_master=semisync_master.so;rpl_semi_sync_slave=semisync_slave.so"
rpl_semi_sync_master_enabled = 1
rpl_semi_sync_slave_enabled = 0
rpl_semi_sync_master_wait_for_slave_count = 1
rpl_semi_sync_master_wait_no_slave = 0
rpl_semi_sync_master_timeout = 300000 # 5 minutes

# CLIENT_DEPRECATE_EOF
session_track_schema = 1
session_track_state_change = 1
session_track_system_variables = '*'

# MISC
log_timestamps=SYSTEM
lower_case_table_names = 1
max_allowed_packet = 64M
read_only = 0
skip_external_locking = 1
skip_name_resolve = 1
skip_slave_start = 1
socket = mysqld.sock
pid_file = mysqld.pid
disabled_storage_engines = ARCHIVE,BLACKHOLE,EXAMPLE,FEDERATED,MEMORY,MERGE,NDB
log-output = TABLE,FILE
character_set_server = utf8mb4
secure_file_priv = ""
performance-schema-instrument='wait/lock/metadata/sql/mdl=ON'
expire_logs_days = 14

# MTS
slave-parallel-type=LOGICAL_CLOCK
slave_parallel_workers=16
slave_preserve_commit_order=1
"""
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
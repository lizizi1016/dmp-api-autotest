from behave import *
from framework.api import *
import pyjq
import json
import time
from datetime import datetime
from util import *
use_step_matcher("cfparse")

@when(u'I found a MySQL instance without backup rule, or I skip the test')
def step_impl(context):
	mysqls = api_get(context, "database/list_instance", {
		"number": context.page_size_to_select_all,
	})
	mysql_ids = pyjq.all('.data[] | .mysql_id', mysqls)

	for mysql_id in mysql_ids:
		resp = api_get(context, "urman_rule/list_backup_rule", {
			mysql_id: mysql_id,
		})
		if len(resp["data"]) == 0:
			context.mysql_instance = pyjq.first('.data[] | select(.mysql_id = "{0}")'.format(mysql_id), mysqls)
			return
	context.scenario.skip("Found no MySQL instance without backup rule")

@when(u'I add a backup rule to the MySQL instance, which will be triggered in {delta_minutes:int}m')
def step_impl(context, delta_minutes):
	assert context.mysql_instance != None
	mysql = context.mysql_instance

	ts = datetime.now()
	newMinute = (ts.minute + delta_minutes * context.time_weight) % 60
	cron = "0 {0} * * * ?".format(newMinute)
	backup_rule_id = "rule_" + mysql["mysql_id"]
	
	resp = api_post(context, "urman_rule/add_backup_rule", {
        "backup_rule_id": backup_rule_id,
        "instance_id": mysql["mysql_id"],
        "server_id": mysql["server_id"],
        "full_backup_cron": cron,
        "increment_backup_cron": "",
        "backup_remains": "2",
        "backup_priority": "99",
        "maintain_start_cron": "0 0 0 1/1 * ?",
        "maintain_duration_time": "1440m",
        "backup_tool": "XtraBackup",
        "backup_cnf":'''[global]
backup_lock_path = ./backup_lock
[mysql_backup]
xb_defaults = --use-memory=200MB --tmpdir={} --ftwrl-wait-timeout=120 --ftwrl-wait-threshold=120 --kill-long-queries-timeout=60 --kill-long-query-type=all --ftwrl-wait-query-type=all --no-version-check
xb_backup_to_image = --defaults-file={} --host={} --port={} --user={} --compress --throttle=300 --no-timestamp --stream=xbstream
xb_incremental_backup_to_image = --defaults-file={} --host={} --port={} --user={} --incremental --incremental-lsn={} --compress --throttle=300 --no-timestamp --stream=xbstream
xb_image_to_backup_dir = -x
xb_decompress = --decompress
xb_full_apply_log = --defaults-file={} --apply-log
xb_apply_incremental_backup = --defaults-file={} --apply-log --incremental-dir={}
xb_copy_back = --defaults-file={} --force-non-empty-directories --move-back

xb_backup_to_image_timeout_seconds = 21600
xb_incremental_backup_to_image_timeout_seconds = 21600
xb_image_to_backup_dir_timeout_seconds = 21600
xb_decompress_seconds = 21600
xb_full_apply_log_timeout_seconds = 21600
xb_apply_incremental_backup_timeout_seconds = 21600
xb_copy_back_timeout_seconds = 21600
''',
		"only_slave": "false",
		"only_master": "false"
    })
	
	api_request_post(context, "urman_rule/confirm_add_backup_rule", {
        "config-id": get_3pc_config_id(resp),
        "is-commit": "true",
        "backup_rule_id": backup_rule_id,
    })

@then(u'the MySQL instance should have a backup rule')
def step_impl(context):
	assert context.mysql_instance != None
	mysql = context.mysql_instance
	mysql_id = mysql["mysql_id"]

	resp = api_get(context, "urman_rule/list_backup_rule", {
		"instance_id": mysql_id,
	})
	
	has_match = pyjq.first('.data | any(."instance_id" == "{0}")'.format(mysql_id), resp)
	assert has_match

@then(u'the MySQL instance should have a new backup set in {duration:time}')
def step_impl(context, duration):
	assert context.mysql_instance != None
	mysql = context.mysql_instance
	mysql_id = mysql["mysql_id"]

	resp = api_get(context, "urman_backupset/list", {
		"instance": mysql_id,
	})
	origin_id = pyjq.first('.data[] | .backup_set_id'.format(mysql_id), resp)

	for i in range(1, duration * context.time_weight):
		resp = api_get(context, "urman_backupset/list", {
			"instance": mysql_id,
		})
		id = pyjq.first('.data[] | .backup_set_id'.format(mysql_id), resp)
		if id != origin_id:
			return
		time.sleep(1)
	assert False

@when(u'I found a backup rule, or I skip the test')
def step_impl(context):
	resp = api_get(context, "urman_rule/list_backup_rule", {
		"number": context.page_size_to_select_all,
	})
	rule = pyjq.first('.data[0]', resp)

	if rule == None:
		context.scenario.skip("Found no backup rule")
	else:
		context.backup_rule = rule

@when(u'I found the MySQL instance of the backup rule')
def step_impl(context):
	assert context.backup_rule != None

	mysqls = api_get(context, "database/list_instance", {
		"mysql_id": context.backup_rule["instance_id"],
	})
	assert len(mysqls["data"]) == 1
	context.mysql_instance = mysqls["data"][0]

@when(u'I remove the backup rule')
def step_impl(context):
	assert context.backup_rule != None

	backup_rule_id = context.backup_rule["backup_rule_id"]

	resp = api_post(context, "urman_rule/remove_backup_rule", {
		"backup_rule_id": backup_rule_id,
	})
	
	api_request_post(context, "urman_rule/confirm_remove_backup_rule", {
        "config-id": get_3pc_config_id(resp),
        "is-commit": "true",
        "backup_rule_id": backup_rule_id,
    })

@then(u'the backup rule should not exist')
def step_impl(context):
	assert context.backup_rule != None
	backup_rule_id = context.backup_rule["backup_rule_id"]

	resp = api_get(context, "urman_rule/list_backup_rule", {
		"number": context.page_size_to_select_all,
	})
	has_match = pyjq.first('.data | any(."backup_rule_id" == "{0}")'.format(backup_rule_id), resp)

	assert not has_match

def get_3pc_config_id(resp):
    idx = resp['raw'].rindex('{"config-id"')
    obj = json.loads(resp['raw'][idx:])
    config_id = obj['config-id']
    assert config_id != None
    return config_id

@when(u'I recycle the backup dir of the MySQL instance')
def step_impl(context):
	assert context.mysql_instance != None
	mysql = context.mysql_instance
	mysql_id = mysql["mysql_id"]

	api_request_post(context, "urman_rule/recycle_backup_dir", {
		"instance_id": mysql_id,
        "rule_type": "backup_tool_rule",
        "is_sync": "true",
	})

@then(u'the backup dir of the MySQL instance should not exist')
def step_impl(context):
	assert context.mysql_instance != None
	mysql = context.mysql_instance
	mysql_id = mysql["mysql_id"]
	server_id = mysql["server_id"]
	backup_path = mysql["backup_path"]

	resp = api_get(context, "helper/ll", {
        "server_id": server_id,
        "path": backup_path,
    })

	assert len(resp) == 0



@when(u'I update the backup rule, make it will be triggered in {delta_minutes:int}m')
def step_impl(context, delta_minutes):
	assert context.backup_rule != None
	backup_rule_id = context.backup_rule["backup_rule_id"]

	assert context.mysql_instance != None
	mysql = context.mysql_instance

	ts = datetime.now()
	newMinute = (ts.minute + delta_minutes * context.time_weight) % 60
	cron = "0 {0} * * * ?".format(newMinute)

	cnf = api_get(context, "support/read_umc_file", {
		"path": "backupcnfs/backup.xtrabackup", 
	})
	
	resp = api_post(context, "urman_rule/update_backup_rule", {
        "backup_rule_id": backup_rule_id,
        "instance_id": mysql["mysql_id"],
        "server_id": mysql["server_id"],
        "full_backup_cron": cron,
        "increment_backup_cron": "",
        "backup_remains": "2",
        "backup_priority": "99",
        "maintain_start_cron": "0 0 0 1/1 * ?",
        "maintain_duration_time": "1440m",
        "backup_tool": "XtraBackup",
        "backup_cnf": cnf,
		"only_slave": "false",
		"only_master": "false"
    })
	
	api_request_post(context, "urman_rule/confirm_update_backup_rule", {
        "config-id": get_3pc_config_id(resp),
        "is-commit": "true",
        "backup_rule_id": backup_rule_id,
    })


@then(u'the MySQL instance manual backup list should contains the urman backup set in {duration:time}')
def step_impl(context, duration):
	assert context.mysql_instance != None
	mysql_id = context.mysql_instance["mysql_id"]
	resp = api_get(context, "urman_backupset/list", {
		"instance": mysql_id,
	})
	origin_id = pyjq.first('.data[] | .backup_set_id', resp)
	def condition(context, flag):
		resp = api_get(context, "urman_backupset/list", {
			"instance": mysql_id,
		})
		id = pyjq.first('.data[] | .backup_set_id', resp)
		if id != origin_id:
			return True
	waitfor(context, condition, duration)


from behave import *
from framework.api import *
import pyjq
import json
import time
from datetime import datetime

use_step_matcher("cfparse")

@when(u'I found a MySQL instance without backup rule, or I skip the test')
def step_impl(context):
	#TODO
    match = {
    	"instance_id": "mysql-taxb4w",
    	"server_id": "server-udp2",
    }
    if match is None:
        context.scenario.skip("Found no MySQL instance without backup rule")
    else:
    	context.mysql_instance = match


@when(u'I add a backup rule to the MySQL instance, which will be triggered in {delta_minutes:int}m')
def step_impl(context, delta_minutes):
	assert context.mysql_instance != None
	mysql = context.mysql_instance

	ts = datetime.now()
	newMinute = (ts.minute + delta_minutes * context.time_weight) % 60
	cron = "0 {0} * * * ?".format(newMinute)
	backup_rule_id = "rule_" + mysql["instance_id"]
	
	resp = api_post(context, "urman_rule/add_backup_rule", {
        "backup_rule_id": backup_rule_id,
        "instance_id": mysql["instance_id"],
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

	idx = resp['raw'].rindex('{"config-id"')
	obj = json.loads(resp['raw'][idx:])
	config_id = obj['config-id']
	assert config_id != None
	
	api_request_post(context, "urman_rule/confirm_add_backup_rule", {
        "config-id": config_id,
        "is-commit": "true",
        "backup_rule_id": backup_rule_id,
    })

@then(u'the MySQL instance should have a backup rule')
def step_impl(context):
	assert context.mysql_instance != None
	mysql = context.mysql_instance
	mysql_id = mysql["instance_id"]

	resp = api_get(context, "urman_rule/list_backup_rule", {
		"instance_id": mysql_id,
	})
	
	has_match = pyjq.first('.data | any(."instance_id" == "{0}")'.format(mysql_id), resp)
	assert has_match

@then(u'the MySQL instance should have a new backup set in {duration:time}')
def step_impl(context, duration):
	assert context.mysql_instance != None
	mysql = context.mysql_instance
	mysql_id = mysql["instance_id"]

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


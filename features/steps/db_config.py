from behave import *
from framework.api import *
import pyjq
import time
import json

use_step_matcher("cfparse")

@when(u'I update MySQL configuration "{option:string}" to "{option_value:string}"')
def step_impl(context, option, option_value):
	assert context.mysql_instance != None
	mysql = context.mysql_instance

	query_resp = api_post(context, "modify_config/query", {
		"super_user": "root",
		"super_password": mysql["root_password"],
		"mysql_connect_type": "socket",
		"mysql_ids": mysql["mysql_id"],
		"option": option,
		"option_value": option_value,
	})

	condition = '.[] | select(."option" == "{0}")'.format(option)
	assert len(pyjq.all(condition, query_resp)) == 1

	api_request_post(context, "modify_config/save", {
    	"config": json.dumps(query_resp),
    	"is_sync": True,
	})


@when(u'I wait for updating MySQL configuration finish in {duration:time}')
def step_impl(context, duration):
	for i in range(1, duration * context.time_weight * 10):
		resp = api_get(context, "modify_config/query_result")
		condition = '. | any(select(."result" == "processing") or (has("result") | not))'
		any_processing = pyjq.first(condition, resp)
		if not any_processing:
			return
		time.sleep(0.1)
	assert False
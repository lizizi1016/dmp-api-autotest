current_path = $(shell pwd)
default: prepare test
prepare:
	behave features/prepare.feature
test:
	behave  features/server.feature features/mysql_e2e_base.feature features/db_config.feature features/urman.feature features/sippool.feature features/ushard.feature features/destructive_test_cases.feature
install_deps:
	pip install -r requirements.txt
env_dmp:
	cd ${current_path}/deploy && make install
format: 
	yapf --recursive --in-place --style='{based_on_style: google, indent_width: 4}' .

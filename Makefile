default: prepare test
prepare: 
	behave features/prepare.feature
test:
	behave features/server.feature features/sippool.feature features/db_config.feature features/urman.feature features/database.feature
install_deps:
	pip install -r requirements.txt
format: 
	yapf --recursive --in-place --style='{based_on_style: google, indent_width: 4}' .

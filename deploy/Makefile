PWD = $(shell pwd)
TARGET_DOCKER_TMP_DIR = "/tmp/deploy"
TARGET_DOCKER = "udp-1"
CENTOS_DOCKER_COMPOSE_FILE = docker-compose.yaml

install: docker_up
	docker exec ${TARGET_DOCKER} rm -rf ${TARGET_DOCKER_TMP_DIR}
	docker cp ${PWD} ${TARGET_DOCKER}:${TARGET_DOCKER_TMP_DIR}
	docker exec -t ${TARGET_DOCKER} bash -c "bash ${TARGET_DOCKER_TMP_DIR}/udp_install.sh"

docker_up: clean
	cd ${PWD}/compose && docker-compose -f ${CENTOS_DOCKER_COMPOSE_FILE} up -d

clean:
	cd ${PWD}/compose && docker-compose -f ${CENTOS_DOCKER_COMPOSE_FILE} down
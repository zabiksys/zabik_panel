### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# .env de la raíz (compartido con start.sh) y .env local de devops.
# Rutas robustas: funcionan tanto desde devops/ como con `make -f devops/Makefile`.
DEVOPS_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
ROOT_DIR := $(abspath $(DEVOPS_DIR)/..)
include $(ROOT_DIR)/.env
include $(DEVOPS_DIR)/.env
export

ifndef DEPLOY_ENV
$(error DEPLOY_ENV is not set)
endif

ifndef DEPLOY_USER
$(error DEPLOY_USER is not set)
endif

ifndef DEPLOY_SCALES
	DEPLOY_SCALES=2
endif

ifeq ($(DEPLOY_ENV), dev)
	CONTEXT=dev
	CONTEXT_HOST=ssh://$(DEPLOY_USER)@$(DEPLOY_HOST):$(DEPLOY_PORT)
else ifeq ($(DEPLOY_ENV), prod)
	CONTEXT=prod
	CONTEXT_HOST=ssh://$(DEPLOY_USER)@$(DEPLOY_HOST):$(DEPLOY_PORT)
else
$(error DEPLOY_ENV is not supported)
endif

DOCKER=docker
DOCKER_CMD_CONTEXT=${DOCKER} --context ${CONTEXT}

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: ## remove all build, test, coverage and Python artifacts
	@echo "$(GREEN)==> Clean up the installation$(RESET)"
	rm -Rf bin lib lib64 include pyvenv.cfg .docker

bin/pip:
	@echo "$(GREEN)==> Python: Setup Virtual Env$(RESET)"
	python3 -m venv .
	bin/pip install -U pip pipx

bin/ansible:

.PHONY: setup
setup: bin/pip ## Ansible: Install Ansible and dependencies
	@echo "$(GREEN)==> Ansible: Install Ansible and dependencies $(RESET)"
	bin/pip install -r requirements/requirements.txt --upgrade
	bin/ansible-galaxy install -r requirements/roles.yml --force --no-deps
	bin/ansible-galaxy collection install -r requirements/collections.yml

.PHONY: server-setup
server-setup: bin/ansible ## Server: Configure a remote server
	@echo "$(GREEN)==> Server: Configure a remote server with Ansible$(RESET)"
	./bin/ansible-playbook playbooks/setup.yml --limit ${CONTEXT}

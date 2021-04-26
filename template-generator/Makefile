# Makefile used to run Template Generator

PACKAGE_DIR := template_generator

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  'all'  build all cloud templates and readme files"
	@echo "  'gce'  build google cloud templates and readme files"
	@echo "  'azure'  build azure cloud templates and readme files"

lint:
	echo "Running linter (any error will result in non-zero exit code)";
	pylint ${PACKAGE_DIR}/;
	flake8 ${PACKAGE_DIR}/

.PHONY: gce
gce:
	build/generate_templates.sh --gce

.PHONY: azure
azure:
	build/generate_templates.sh --azure

.PHONY: all
all:
	build/generate_templates.sh --azure --gce

.PHONY: release
release:
	build/generate_templates.sh --azure --gce --release-prep
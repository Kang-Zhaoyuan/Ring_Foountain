QCC := /home/kqdx/basilisk/src/qcc
BASILISK := /home/kqdx/basilisk/src
CASE ?= cases/00_official_missing_metric
BUILD_DIR := $(CASE)/build
SOURCE := $(firstword $(wildcard $(CASE)/source_run.c $(CASE)/main.c $(CASE)/*.c))
SOURCE_NAME := $(notdir $(SOURCE))
PROGRAM := $(BUILD_DIR)/case.exe
PROGRAM_ABS := $(abspath $(PROGRAM))

.PHONY: env-check build run validate open-latest git-status
env-check:
	./scripts/env_check.sh
build:
	@test -n "$(SOURCE)" || (echo "No C source in $(CASE)" >&2; exit 2)
	mkdir -p "$(BUILD_DIR)"
	(cd "$(CASE)" && $(QCC) -O2 -Wall $(QCC_FLAGS) "$(SOURCE_NAME)" -o "$(PROGRAM_ABS)" -lm)
run:
	./scripts/run_case.sh "$(CASE)"
validate:
	./scripts/validate_case.sh "$(CASE)"
open-latest:
	@find runs -maxdepth 1 -mindepth 1 -type d | sort | tail -n 1
git-status:
	@git status --short --branch

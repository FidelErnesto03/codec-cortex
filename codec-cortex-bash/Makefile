SHELL := /usr/bin/env bash
ROOT := $(CURDIR)
BIN := $(ROOT)/bin/codec-cortex
F3 := $(ROOT)/tests/conformance/gate-f3/c14n-corpus
F4 := $(ROOT)/tests/conformance/gate-f4

.PHONY: test syntax phase3 phase4 conformance install

test: syntax
	$(ROOT)/tests/self-test.sh

syntax:
	bash -n $(ROOT)/bin/codec-cortex $(ROOT)/lib/codec-cortex.sh $(ROOT)/tests/self-test.sh

phase3:
	$(BIN) phase3 $(F3)

phase4:
	$(BIN) phase4 $(F4)

conformance:
	$(BIN) test $(F3) $(F4) $(ROOT)/conformance-report.json

install:
	$(ROOT)/install.sh

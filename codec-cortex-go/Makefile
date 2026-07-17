.PHONY: test vet build clean differential dist

BINARY ?= bin/codec-cortex

all: test build

test:
	go test ./...

vet:
	go vet ./...

build:
	go build -trimpath -ldflags="-s -w" -o $(BINARY) ./cmd/codec-cortex

differential:
	./scripts/differential_check.sh

dist:
	./scripts/build_dist.sh

clean:
	rm -rf bin/* rev-report.json

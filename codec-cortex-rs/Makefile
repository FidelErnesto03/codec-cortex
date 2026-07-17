.PHONY: check test release differential

check:
	cargo check --all-targets
	cargo clippy --all-targets --all-features

test:
	cargo test --all-targets

release:
	cargo build --release

differential:
	@test -n "$(PYTHON_ROOT)" || (echo "PYTHON_ROOT is required" && exit 2)
	cargo build
	python tools/differential.py --python-root "$(PYTHON_ROOT)" --rust-bin target/debug/cortex tests/fixtures/roundtrip.cortex examples/full.cortex

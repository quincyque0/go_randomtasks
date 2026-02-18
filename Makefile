WEEK ?= 01

.PHONY: test

test:
	python -m pytest -q weeks/week-$(WEEK)/tests

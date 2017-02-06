TESTS := tests/

test:
	PYTHONPATH=. pytest $(TESTS)

coverage:
	PYTHONPATH=. pytest --cov=camisole $(TESTS)

coverage-html: coverage
	coverage html

.PHONY: test coverage coverage-html

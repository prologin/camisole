TESTS := tests/

test:
	PYTHONPATH=. pytest $(TESTS)

coverage:
	PYTHONPATH=. pytest --cov=camisole $(TESTS)

coverage-html: coverage
	coverage html

upload:
	python setup.py bdist
	twine upload dist/*

.PHONY: test coverage coverage-html

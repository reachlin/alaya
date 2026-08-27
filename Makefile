.PHONY: test watch clean

test:
	python -m pytest

watch:
	python -m pytest -q --looponfail 2>/dev/null || python -m pytest

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} + ; rm -rf .pytest_cache

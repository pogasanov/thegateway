.PHONY: docs

docs:
	python -m mkdocs build --clean --site-dir _build/html --config-file mkdocs.yml


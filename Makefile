.PHONY: install-importers develop-importers install-lint-dep lint-test test docs

install-importers:
	pip install ./gateway_pkg ./prestashop_pkg ./sellingo_pkg ./idosell_pkg ./magento_pkg ./shoper_pkg ./wordpress_pkg

develop-importers:
	pip install -e ./gateway_pkg
	pip install -e ./prestashop_pkg -e ./sellingo_pkg -e ./idosell_pkg -e ./magento_pkg -e ./shoper_pkg -e ./wordpress_pkg

install-lint-dep:
	pip install -e ./gateway_pkg
	pip install -e ./prestashop_pkg -e ./sellingo_pkg -e ./idosell_pkg -e ./magento_pkg -e ./shoper_pkg -e ./wordpress_pkg
	pip install -r requirements.txt

lint-test:
	black --check .
	pylint-fail-under --fail_under 7.0 ${PWD}
	# this can be changed after reaching 10/10 score

test:
	py.test --cov=. -v

docs:
	python -m mkdocs build --clean --site-dir _build/html --config-file mkdocs.yml

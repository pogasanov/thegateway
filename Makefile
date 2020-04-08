install-importers:
	pip install ./gateway_pkg ./prestashop_pkg

install-lint-dep:
	pip install -r requirements.txt

lint-test:
	black --check .
	pylint-fail-under --fail_under 7.0 ${PWD}
	# this can be changed after reaching 10/10 score

test:
	coverage run -m unittest
	coverage report

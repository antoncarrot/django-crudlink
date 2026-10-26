all: format

.PHONY: format
format: py-format js-format

.PHONY: lint
lint: py-lint js-lint

.PHONY: test
test: py-test js-test

# What CI runs
.PHONY: check
check: lint js-type-check test js-build

# Python

.PHONY: py-test
py-test:
	pytest

.PHONY: py-lint
py-lint:
	ruff check

.PHONY: py-format
py-format:
	ruff check --fix --select I,RUF022
	ruff format

# Update the translation catalogs from the code, then compile them (the .mo files are committed)
.PHONY: py-locale
py-locale:
	cd django_crudlink && django-admin makemessages -l en -l ru --ignore "tests/*" --no-location --no-obsolete
	cd django_crudlink && django-admin compilemessages

# Frontend

.PHONY: js-test
js-test:
	npm test

.PHONY: js-lint
js-lint:
	npm run lint

.PHONY: js-format
js-format:
	npm run format

.PHONY: js-type-check
js-type-check:
	npm run type-check

.PHONY: js-build
js-build:
	npm run build:django

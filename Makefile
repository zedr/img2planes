.PHONY: default clean install test

ENV=.env
_PYTHON=python3
PYTHON_VERSION=$(shell ${_PYTHON} -V | cut -d " " -f 2 | cut -d "." -f1-2)
SITE_PACKAGES=${ENV}/lib/python${PYTHON_VERSION}/site-packages
PYTHON=${ENV}/bin/python3
IN_ENV=source ${ENV}/bin/activate ;

default: ${PYTHON}

${PYTHON}:
	@echo "Creating Python ${PYTHON_VERSION} environment..." >&2
	@${_PYTHON} -m venv ${ENV}
	@${PYTHON} -m pip install -U pip wheel

install: ${PYTHON}
	@echo "Installing img2planes in local virtualenv" >&2
	@${PYTHON} -m pip install .

test: ${PYTHON} install
	@${PYTHON} setup.py test

clean:
	@rm -rf .env

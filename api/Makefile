init:
	pre-commit install

migrate:
	echo "start migrating (without any backup)."
	alembic upgrade heads
	echo "done migrating."

update-requirements:
	pip-compile --output-file requirements.txt requirements.in

clean:
	rm -rf .pytest_cache/
	rm -rf coverage_html/
	find . -iname "*__pycache__" | xargs rm -rf
	find . -iname "*.pyc" | xargs rm -rf
	rm -f .coverage
	rm -f .DS_Store
	rm -f cobertura.xml
	rm -f testresult.xml
	rm -rf build
	rm -rf cov_html
	rm -rf dist
	rm -rf *.egg-info

test: clean
	export REDIS_HOST="127.0.0.1"; \
	export REDIS_PORT="6379"; \
	pytest -rs -vvvv --durations 10 --disable-pytest-warnings --cov-report term-missing --cov-report html:coverage_html --cov=app/ .

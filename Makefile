init:
	pre-commit install

dev:
	docker compose -f docker-compose.dev.yaml --env-file .docker-compose.dev.env down
	docker compose -f docker-compose.dev.yaml --env-file .docker-compose.dev.env up -d

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
	echo "testing..."

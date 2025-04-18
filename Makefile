build:
	poetry build
publish:
	# poetry config pypi-token.pypi <your-api-token>
	poetry publish --build 
lint:
	poetry run black . 
	poetry run flake8 
dev:
	poetry run marimo edit dev.py

server:
	env PYTHONPATH=$(PWD) poetry run python -m literate_python 

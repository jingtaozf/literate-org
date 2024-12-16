build:
	poetry build
publish:
	# poetry config pypi-token.pypi <your-api-token>
	poetry publish --build 
dev:
	poetry run marimo edit dev.py

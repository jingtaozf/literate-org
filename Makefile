install-kernel:
	@echo "Installing kernel..."
	poetry run ipython kernel install --user --name=literate-python
jupyter:
	poetry run jupyter lab --ServerApp.disable_check_xsrf=True  --ServerApp.allow_remote_access=True --KernelSpecManager.ensure_native_kernel=False --ServerApp.terminals_enabled=False --ServerApp.allow_origin="*"  --no-browser
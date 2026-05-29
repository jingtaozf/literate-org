build:
	poetry build
publish:
	# poetry config pypi-token.pypi <your-api-token>
	poetry publish --build 
lint:
	poetry run black .
	poetry run flake8

check-structure:
	python3 scripts/check_org_structure.py

check-nl-outline:
	python3 scripts/check_nl_outline.py

check-dead-code:
	poetry run vulture

tangle:
	@if [ -z "$(FILE)" ]; then \
	  echo "usage: make tangle FILE=path/to/file.org" >&2; exit 2; \
	fi
	@if [ ! -f "$(FILE)" ]; then \
	  echo "make tangle: $(FILE) does not exist" >&2; exit 2; \
	fi
	emacs --batch \
	  --eval "(require (quote org))" \
	  --eval "(setq org-confirm-babel-evaluate nil)" \
	  --eval "(org-babel-tangle-file \"$(FILE)\")"
	poetry run black --quiet literate_python/ 2>/dev/null || true

index:
	python3 scripts/build_index.py

# One-shot full-history secret scan (gitleaks). Per-commit scan runs via
# pre-commit. Use this on first install to baseline existing history,
# and ad-hoc when investigating a leak alert.
secret-scan:
	pre-commit run gitleaks --all-files

dev:
	poetry run marimo edit dev.py

server:
	env PYTHONPATH=$(PWD) poetry run python -m literate_python 

# ── Terraform/HCL E2E tests (added with terraform language support) ──
EMACS ?= emacs

# Optional real-world sweep: point at a production .tf tree to assert
# every file partitions byte-complete. Unset → that one test skips.
#   make test-terraform LITERATE_ORG_TF_SAMPLE_DIR=/path/to/mega-code-infra
export LITERATE_ORG_TF_SAMPLE_DIR

.PHONY: test test-terraform

## Run the Terraform/HCL ert tests embedded in literate-org.org.
test-terraform:
	$(EMACS) -Q --batch -L . -l tests/run-tests.el \
		-f ert-run-tests-batch-and-exit literate-org-terraform

## Run every embedded ert test.
test:
	$(EMACS) -Q --batch -L . -l tests/run-tests.el \
		-f ert-run-tests-batch-and-exit

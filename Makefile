# Root Makefile for the generated Zettel Wiki software inventory page.
# Assumes the Wiki repository is cloned beside this repository as ../Zettel.wiki.

PYTHON ?= python
WIKI_DIR ?= ../Zettel.wiki
POWERSHELL ?= powershell

MANIFEST := MANIFEST.software.yaml
GENERATOR := python/gen_software_components.py
PUBLISH_SCRIPT := scripts/publish-software-inventory.ps1
PUBLISH_CMD := scripts/publish-software-inventory.cmd
GENERATED_DIR := generated
PAGE_FILE := Zettelkasten-software-inventory.md
GENERATED_PAGE := $(GENERATED_DIR)/$(PAGE_FILE)

MAIN_FILES := Makefile \
	$(MANIFEST) \
	$(GENERATOR) \
	python/test_gen_software_components.py \
	python/test_manifest_repository_files.py \
	python/zettel_diagnostics.py \
	python/test_zettel_diagnostics.py \
	$(PUBLISH_SCRIPT) \
	$(PUBLISH_CMD) \
	doc/publish-software-inventory.ps1.md \
	doc/publish-software-inventory.cmd.md \
	doc/test_gen_software_components.py.md \
	doc/test_manifest_repository_files.py.md \
	doc/zettel_diagnostics.py.md \
	$(GENERATED_PAGE)
MAIN_COMMIT_MSG ?= Generate software inventory page
WIKI_COMMIT_MSG ?= Update software inventory page
PUBLISH_ARGS := -NoProfile -ExecutionPolicy Bypass -File "$(PUBLISH_SCRIPT)" -Python "$(PYTHON)" -WikiDir "$(WIKI_DIR)" -WikiCommitMessage "$(WIKI_COMMIT_MSG)"

.PHONY: help generate copy-wiki diff-wiki commit-wiki push-wiki publish-wiki commit-main push-main publish-all status clean-generated clean-obsolete-generated

help:
	@echo "Targets:"
	@echo "  make generate                Generate $(GENERATED_PAGE)"
	@echo "  make copy-wiki               Generate and copy through $(PUBLISH_SCRIPT) -DiffOnly"
	@echo "  make diff-wiki               Show Wiki diff after copying"
	@echo "  make publish-wiki            Generate, copy, commit Wiki page, and push Wiki repo"
	@echo "  make commit-main             Commit current generated source/output files in main repo"
	@echo "  make push-main               Commit and push current main repo changes"
	@echo "  make publish-all             Commit Wiki page, push main repo changes, then push Wiki repo"
	@echo "  make clean-obsolete-generated Remove obsolete generated software page names"
	@echo "  Windows: .\\scripts\\publish-software-inventory.cmd"
	@echo "Variables:"
	@echo "  WIKI_DIR=$(WIKI_DIR)"
	@echo "  PYTHON=$(PYTHON)"
	@echo "  POWERSHELL=$(POWERSHELL)"

generate:
	$(PYTHON) "$(GENERATOR)" --manifest "$(MANIFEST)" --repo . --out "$(GENERATED_PAGE)"

copy-wiki:
	$(POWERSHELL) $(PUBLISH_ARGS) -DiffOnly

diff-wiki: copy-wiki

commit-wiki:
	$(POWERSHELL) $(PUBLISH_ARGS) -NoPush

push-wiki:
	$(POWERSHELL) $(PUBLISH_ARGS)

publish-wiki: push-wiki

commit-main:
	git add $(MAIN_FILES)
	git diff --cached --quiet -- $(MAIN_FILES) || git commit -m "$(MAIN_COMMIT_MSG)" -- $(MAIN_FILES)

push-main: commit-main
	git push

publish-all:
	$(POWERSHELL) $(PUBLISH_ARGS) -NoPush
	git add $(MAIN_FILES)
	git diff --cached --quiet -- $(MAIN_FILES) || git commit -m "$(MAIN_COMMIT_MSG)" -- $(MAIN_FILES)
	git push
	git -C "$(WIKI_DIR)" push

status:
	git status --short
	git -C "$(WIKI_DIR)" status --short

clean-generated:
	$(PYTHON) -c "from pathlib import Path; import sys; [Path(p).unlink(missing_ok=True) for p in sys.argv[1:]]; [print(f'Removed {p}') for p in sys.argv[1:]]" "$(GENERATED_PAGE)"

clean-obsolete-generated:
	$(PYTHON) -c "from pathlib import Path; import sys; [Path(p).unlink(missing_ok=True) for p in sys.argv[1:]]; [print(f'Removed {p}') for p in sys.argv[1:]]" generated/Zettelkasten-software-components.md generated/Zettelkasten-software-environment-and-repository-tools.md generated/Zettelkasten-software-configuration.md

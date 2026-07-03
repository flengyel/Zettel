# Root Makefile for generated Zettel Wiki software-environment page.
# Assumes the Wiki repository is cloned beside this repository as ../Zettel.wiki.

PYTHON ?= python
WIKI_DIR ?= ../Zettel.wiki

MANIFEST := MANIFEST.software.yaml
GENERATOR := python/gen_software_components.py
GENERATED_DIR := generated
PAGE_FILE := Zettelkasten-software-environment-and-repository-tools.md
GENERATED_PAGE := $(GENERATED_DIR)/$(PAGE_FILE)
WIKI_PAGE := $(WIKI_DIR)/$(PAGE_FILE)

MAIN_FILES := Makefile $(MANIFEST) $(GENERATOR) $(GENERATED_PAGE)
MAIN_COMMIT_MSG ?= Generate software environment page
WIKI_COMMIT_MSG ?= Update software environment page

.PHONY: help generate copy-wiki diff-wiki commit-wiki push-wiki publish-wiki commit-main push-main publish-all status clean-generated

help:
	@echo "Targets:"
	@echo "  make generate       Generate $(GENERATED_PAGE)"
	@echo "  make copy-wiki      Generate and copy page into $(WIKI_DIR)"
	@echo "  make diff-wiki      Show Wiki diff after copying"
	@echo "  make publish-wiki   Generate, copy, commit Wiki page, and push Wiki repo"
	@echo "  make commit-main    Commit Makefile and generated source/output files in main repo"
	@echo "  make push-main      Commit and push main repo changes"
	@echo "  make publish-all    Push main repo changes and Wiki page update"
	@echo "Variables:"
	@echo "  WIKI_DIR=$(WIKI_DIR)"
	@echo "  PYTHON=$(PYTHON)"

generate:
	$(PYTHON) "$(GENERATOR)" --manifest "$(MANIFEST)" --repo . --out "$(GENERATED_PAGE)"

copy-wiki: generate
	git -C "$(WIKI_DIR)" rev-parse --is-inside-work-tree
	$(PYTHON) -c "from pathlib import Path; import shutil, sys; src=Path(sys.argv[1]); dst=Path(sys.argv[2]) / sys.argv[3]; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst); print(f'Copied {src} -> {dst}')" "$(GENERATED_PAGE)" "$(WIKI_DIR)" "$(PAGE_FILE)"

diff-wiki: copy-wiki
	git -C "$(WIKI_DIR)" diff -- "$(PAGE_FILE)"

commit-wiki: copy-wiki
	git -C "$(WIKI_DIR)" add "$(PAGE_FILE)"
	git -C "$(WIKI_DIR)" diff --cached --quiet -- "$(PAGE_FILE)" || git -C "$(WIKI_DIR)" commit -m "$(WIKI_COMMIT_MSG)" -- "$(PAGE_FILE)"

push-wiki: commit-wiki
	git -C "$(WIKI_DIR)" push

publish-wiki: push-wiki

commit-main: generate
	git add $(MAIN_FILES)
	git diff --cached --quiet -- $(MAIN_FILES) || git commit -m "$(MAIN_COMMIT_MSG)" -- $(MAIN_FILES)

push-main: commit-main
	git push

publish-all: push-main push-wiki

status:
	git status --short
	git -C "$(WIKI_DIR)" status --short

clean-generated:
	$(PYTHON) -c "from pathlib import Path; import sys; p=Path(sys.argv[1]); p.unlink(missing_ok=True); print(f'Removed {p}')" "$(GENERATED_PAGE)"

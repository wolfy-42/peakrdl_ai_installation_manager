#--------------------------------------------------------------------------------------------------
#
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Project      : FPGA Project Template
# Author       : DV
# Created      : 2026-10-28
#--------------------------------------------------------------------------------------------------
# Description  : Installs peakrdl by running install_peakrdl.py in one of these ways:
#                - make              -> shows this list
#                - make venv [PYTHON_VERSION=3.12] -> creates ./uv (the uv tool and the Python
#                                        of that version, downloaded if missing) and an
#                                        empty ./venv from that Python; the install_*
#                                        targets below reuse an existing venv and add the tools
#                - make install_pip_recorded -> option 1a: pip install the cli and exporters from
#                                        PyPI at the recorded versions, no repos cloned
#                - make install_pip_latest   -> option 1b: the same from PyPI at the newest
#                                        versions, no repos cloned
#                - make install_clone -> option 2: git clone all repos, check out the recorded
#                                        compatible revisions, pip-install them
#                - make install_zip   -> option 3: unpack peakrdl_repos.zip and pip-install the repos
#                - make install_local -> option 4: only create the venv from the repos already in
#                                        this folder, without touching them
#                - make zip           -> creates peakrdl_repos.zip from the checked-out repos
#                                        as they are (input for option 3)
#                The venv is made from Python 3.12 provided by uv (downloaded into ./uv on
#                first use). To use another Python instead (it needs its development
#                headers): make install_clone PYTHON=/path/to/python3
# Updated      : 2026-11-03 / DV - pip modes: peakrdl-pdflight from GitHub
#                2026-11-01 / DV - recorded revisions (tag or commit); install_pip split into
#                install_pip_recorded and install_pip_latest; zip mode unpacks clean;
#                venv target (Python version via PYTHON_VERSION)
#--------------------------------------------------------------------------------------------------

# folder of this Makefile (absolute, so make can be run from anywhere with -C)
HERE := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# optional: interpreter used to create the venv (empty = the script's default, uv's Python 3.12)
PYTHON ?=

# Python version of a new venv, provided by uv (used by make venv, and by the install_* targets
# when they have to create the venv themselves)
PYTHON_VERSION ?= 3.12

# the script call; the install mode is added by each target
INSTALL = python3 $(HERE)install_peakrdl.py --python-version $(PYTHON_VERSION) $(if $(PYTHON),--python $(PYTHON)) --mode

# These are command names, not files, so make must always run them
.PHONY: help venv install_pip_recorded install_pip_latest install_clone install_zip install_local zip

# Default target (the first one in the file): only lists the options, never installs anything
help:
	@echo "make venv [PYTHON_VERSION=3.12]  create ./uv (uv + that Python) and an empty ./venv from it (install_* reuse it)"
	@echo "make install_pip_recorded  option 1a: pip install from PyPI at the recorded versions (no repos cloned)"
	@echo "make install_pip_latest    option 1b: pip install from PyPI at the newest versions (no repos cloned)"
	@echo "make install_clone         option 2: git clone the repos, check out the recorded revisions, install"
	@echo "make install_zip           option 3: delete the repos, unpack them clean from peakrdl_repos.zip, install"
	@echo "make install_local         option 4: create the venv from the repos already here, untouched"
	@echo "make zip                   create peakrdl_repos.zip from the checked-out repos"
	@echo "optional: PYTHON=/path/to/python3 to use another interpreter than uv's Python 3.12 for the venv"

#--------------------------------------------------------------------------------------------------
# venv - create the Python and the virtual environment, without the RDL tools
#   Needs: internet access the first time.
#   1. Creates ./uv if missing: downloads the uv tool and, with it, the Python PYTHON_VERSION
#      (default 3.12) into ./uv/python. This Python is the base the venv runs on, so ./uv must
#      be kept (it is gitignored, and recreated by this target or any install_* target).
#   2. Creates ./venv from that Python, with no packages. Stops if ./venv already exists
#      (delete it first). The install_* targets then reuse this venv and install the RDL tools
#      into it. Example: make venv PYTHON_VERSION=3.11
#--------------------------------------------------------------------------------------------------
venv:
	$(INSTALL) venv

#--------------------------------------------------------------------------------------------------
# Option 1a - pip_recorded (PyPI, recorded versions)
#   Needs: internet access to PyPI and GitHub. Clones nothing and uses no local repos.
#   Installs peakrdl-cli and each exporter as released packages, pinned to the versions in
#   PIP_PACKAGES in install_peakrdl.py (the same set as the repos; not the "peakrdl"
#   meta-package, which would also pull in IP-XACT). Our own exporter peakrdl-pdflight is not
#   on PyPI: pip installs it straight from https://github.com/wolfy-42/peakrdl-pdflight at its
#   recorded tag. Their third-party dependencies are whatever PyPI offers on the day. Quickest
#   to set up; not editable.
#--------------------------------------------------------------------------------------------------
install_pip_recorded:
	$(INSTALL) pip_recorded

#--------------------------------------------------------------------------------------------------
# Option 1b - pip_latest (PyPI, newest versions)
#   Same packages as option 1a, but without the version pins: pip installs the newest version
#   of each on the day (peakrdl-pdflight: the newest commit of its main branch on GitHub), so the set can change between installs and is not the recorded,
#   compatible set. Use it to try newer releases.
#--------------------------------------------------------------------------------------------------
install_pip_latest:
	$(INSTALL) pip_latest

#--------------------------------------------------------------------------------------------------
# Option 2 - clone (GitHub, recorded versions)
#   Needs: internet access to GitHub (and PyPI for third-party packages such as Jinja2).
#   Clones every repo into this folder, checks out the recorded revision (tag or commit) of each
#   one (the set listed in install_peakrdl.py), and pip-installs them editable, so the source in the
#   cloned folders is what runs and can be patched. Existing clones are reused and moved to the
#   recorded revision. This is the way to refresh the repos, and the source of the zip for option 3.
#--------------------------------------------------------------------------------------------------
install_clone:
	$(INSTALL) clone

#--------------------------------------------------------------------------------------------------
# Option 3 - zip (committed archive, recorded versions)
#   Needs: peakrdl_repos.zip in this folder (it is in git). No GitHub access; PyPI is still
#   used for third-party packages. Deletes the repo folders and unpacks all of them clean from
#   the zip (existing repos are never reused: local changes in them are lost), then
#   pip-installs them editable. The zip holds the full repos with their .git
#   folders, so the unpacked repos are the same as the clones of option 2 (same revisions, same
#   versions) on machines that cannot reach GitHub.
#--------------------------------------------------------------------------------------------------
install_zip:
	$(INSTALL) zip

#--------------------------------------------------------------------------------------------------
# Option 4 - local (repos already in this folder, left untouched)
#   Needs: the repos already in this folder (from option 2, option 3, or any other way); PyPI for
#   third-party packages. Only creates the venv and pip-installs the repos editable. Nothing is
#   cloned, fetched, checked out or unpacked, so the repos stay exactly as they are: any branch,
#   revision or local patch is used as found. Use it to rebuild the venv after deleting it, or to
#   try repos you changed or updated by hand. The repos are not checked against the recorded
#   revisions; a missing repo folder makes pip stop with an error.
#--------------------------------------------------------------------------------------------------
install_local:
	$(INSTALL) local

#--------------------------------------------------------------------------------------------------
# zip - create the archive used by option 3
#   Run it after option 2 (or whenever the recorded versions change). Builds peakrdl_repos.zip
#   from the repos checked out in this folder (only their git-tracked files and .git folders;
#   build files left by the install are not zipped), plus a peakrdl_versions.txt listing the
#   recorded versions and a LICENSE_WARNING.txt (PeakRDL-docx has no license; do not pass the
#   zip on outside the project). The repos are zipped as they are, not checked: make sure each
#   is on its recorded revision (run option 2 first). Commit the new zip afterwards.
#--------------------------------------------------------------------------------------------------
zip:
	$(INSTALL) makezip

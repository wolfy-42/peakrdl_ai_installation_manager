#!/usr/bin/env python3
#--------------------------------------------------------------------------------------------------
#
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Project      : FPGA Project Template
# Author       : DV
# Created      : 2026-10-27
#--------------------------------------------------------------------------------------------------
# Description  : Installs peakrdl into a virtual environment (dev/tools/peakrdl/venv), in one of
#                these ways (--mode):
#                  pip_recorded  option 1a: pip install the cli and the exporters from PyPI, at
#                           the recorded versions in PIP_PACKAGES below. Nothing is cloned.
#                  pip_latest    option 1b: the same packages from PyPI, at the newest versions
#                           PyPI has on the day (can differ between installs). Nothing is cloned.
#                  clone    option 2 (default): git clone all the repos from GitHub, check out the
#                           compatible revisions recorded in REPOS below, pip-install them (editable).
#                  zip      option 3: delete the repo folders, unpack all of them clean from
#                           peakrdl_repos.zip (full repos, with their .git folders, on the
#                           recorded revisions) and pip-install them (editable). No GitHub
#                           access is needed. Local changes in the repos are lost.
#                  local    option 4: only create the venv and pip-install (editable) the repos
#                           already in this folder. The repos are not cloned, checked out,
#                           unpacked, checked or otherwise touched: whatever revision or local
#                           change they have is installed as it is.
#                  makezip  creates peakrdl_repos.zip from the currently checked-out repos (their
#                           git-tracked files and .git folders, no build files; not checked
#                           against the recorded revisions), plus peakrdl_versions.txt and
#                           LICENSE_WARNING.txt (PeakRDL-docx has no license) (input for option 3).
#                This script itself runs on Python 3.6, but the venv is built with Python 3.12
#                provided by uv, which the script downloads into dev/tools/peakrdl/uv on first
#                use (see UV_VERSION/PYTHON_VERSION; use --python to choose another interpreter).
#
#                  venv     creates dev/tools/peakrdl/uv (the uv tool and the Python
#                           --python-version, default 3.12, downloaded if missing) and an
#                           empty venv from that Python; the modes above reuse the venv.
#
#                Usage:  python3 dev/tools/peakrdl/install_peakrdl.py [--mode MODE] [--python-version 3.12] [--python PATH]
#                        (or use the Makefile next to this script)
#                Then:   source dev/tools/peakrdl/venv/bin/activate   (peakrdl is now on PATH)
#                        or run dev/tools/peakrdl/venv/bin/peakrdl directly
# Updated      : 2026-11-01 / DV - added PeakRDL-Markdown and PeakRDL-docx; removed
#                PeakRDL-ipxact, PeakRDL-systemrdl and the peakrdl meta-package;
#                commit-hash pins; mode pip split into pip_recorded and pip_latest; mode zip deletes the
#                repos and unpacks all of them clean with the unzip command; mode local no
#                longer checks the repos (check_local_repos removed); makezip uses the zip
#                command and no longer checks the revisions; the venv Python 3.12 comes
#                from uv (downloaded into dev/tools/peakrdl/uv)
#                2026-11-02 / DV - our own exporter peakrdl-pdflight (OWN_REPOS) is installed
#                from its local folder in every mode, with a warning at the end if it is missing
#                2026-11-03 / DV - peakrdl-pdflight pinned to v0.1.1 in REPOS (cloned, zipped
#                like the others); pip modes install it from GitHub (git+https); a missing
#                folder uninstalls it from the venv before the warning
#--------------------------------------------------------------------------------------------------


# Overview of what this script does (modes clone and zip; mode local skips step 1;
# the pip modes only do steps 2-4 with the PyPI packages, and makezip only builds the zip):
#   1. get the repos: git clone every peakrdl repo from GitHub (full clones, with history and tags)
#      into dev/tools/peakrdl (repos already there are kept) and check out the recorded revision
#      (release tag or commit) of each one listed in REPOS (see the table below); or, in mode zip,
#      delete the repo folders and unpack all of them clean from the zip file
#   2. create a virtual environment (venv) with Python 3.12 from uv (uv and that Python are
#      downloaded into dev/tools/peakrdl/uv the first time)
#   3. pip-install each repo into the venv in "editable" mode (-e): the installed package points
#      at the checked-out source folder, so changes to the repos take effect without reinstalling
#   4. print the installed peakrdl version and its plugins (exporters) as a check
#
# Why full clones: every repo builds its package version from its git tags (setuptools-scm). The
# repos require each other by version (e.g. regblock needs systemrdl-compiler ~= 1.32), so the
# local copy only satisfies that if its tags are present. Otherwise pip would silently download
# the package from PyPI instead of using the checked-out repo. The zip therefore holds the full
# repos, .git folders included, so unpacked repos behave exactly like cloned ones.
#
# Reference: recorded revision of each repo and the other peakrdl repos it requires. These are
# the declared requirements (from each repo's pyproject.toml), not a tested combination.
#
# | Repo                                 | Revision   | Requires from other peakrdl repos        |
# |--------------------------------------|------------|------------------------------------------|
# | systemrdl-compiler                   | v1.33.0    | none                                     |
# | PeakRDL-regblock                     | v1.3.1     | compiler ~= 1.32, peakrdl-cli >= 1.2.3   |
# | PeakRDL-html                         | v2.12.2    | compiler ~= 1.31, peakrdl-cli >= 1.2.3   |
# | PeakRDL-uvm                          | v2.4.0     | compiler ~= 1.31, peakrdl-cli >= 1.2.3   |
# | PeakRDL-cheader                      | v1.1.0     | compiler ~= 1.31, peakrdl-cli >= 1.2.3   |
# | PeakRDL-python (not SystemRDL org)   | 4.0.0      | compiler >= 1.31 (Python >= 3.9.2)       |
# | PeakRDL (peakrdl-cli only)           | v1.5.0     | compiler ~= 1.27                         |
# | PeakRDL-Markdown (GPL-3.0)           | v1.0.3     | compiler ^1.30.1, peakrdl-cli ^1.5.0     |
# | PeakRDL-docx (not SystemRDL org,     | f92b5a0    | compiler >= 1.27, peakrdl (meta-package) |
# |   no tags, no license)               | (commit)   |   (Python >= 3.10)                       |
# | peakrdl-pdflight (our own,           | v0.1.1     | compiler, peakrdl-cli (any version);     |
# |   github.com/wolfy-42)               |            |   reportlab==5.1.0 (PyPI)                |
# |--------------------------------------|------------|------------------------------------------|
# | PeakRDL-ipxact                       | NOT INSTALLED, intentionally: IP-XACT importer/exporter;  |
# |                                      | IP-XACT is not used (rules.md). Was v3.5.0.               |
# | PeakRDL-systemrdl                    | NOT INSTALLED, intentionally: RDL exporter, only needed   |
# |                                      | for format conversion (rules.md). Was v1.0.1.             |
#
# The peakrdl-cli >= x requirements of the official exporters are an optional "cli" extra, not
# a hard dependency. Tightest constraints: regblock needs compiler >= 1.32; PeakRDL-Markdown
# needs peakrdl-cli >= 1.5.0.
#
# Not installed (IP-XACT is not used in this project, see rules.md): PeakRDL-ipxact,
# PeakRDL-systemrdl, and the "peakrdl" meta-package from the PeakRDL repo, which only bundles
# peakrdl-cli with all official exporters (ipxact and systemrdl included). PeakRDL-docx declares
# the meta-package as a dependency but does not use it, so it is installed without its declared
# dependencies and its real ones are installed explicitly (see NO_DEPS below).
#
# PeakRDL-docx has no git tags: it is pinned to the last commit of its main branch (2024-09-19),
# which has the same code as its PyPI release 0.4.7 (the repo still says version 0.4.6).
# Revisions as of 2026-11-01. The REPOS list below pins each repo to the revision in this table.
#
# peakrdl-pdflight (PDF exporter, our own, Apache-2.0 OR MIT): repo
# https://github.com/wolfy-42/peakrdl-pdflight (push: git@github.com:wolfy-42/peakrdl-pdflight.git).
# It is in REPOS like the other repos (cloned, zipped, unpacked). It is not on PyPI, so the pip
# modes install it straight from GitHub (pip install git+https://...), see PIP_GIT below. In the
# other modes it is installed from its folder after the others; if the folder is missing, it is
# uninstalled from the venv (a stale install would break the peakrdl command) and a warning is
# printed at the end, see OWN_REPOS below.

import argparse     # command line options (--mode, --python)
import os           # path handling
import shutil       # shutil.which: find an interpreter on PATH; shutil.rmtree: delete repo folders
import subprocess   # run external commands (git, python, pip, zip, unzip, peakrdl)
import sys          # sys.exit: stop with an error message
import tarfile      # unpack the uv download
import urllib.request  # download uv

# all paths below are relative to the location of this script
PEAKRDL_DIR = os.path.dirname(os.path.abspath(__file__))   # dev/tools/peakrdl (this script and the checked-out repos)
VENV_DIR = os.path.join(PEAKRDL_DIR, "venv")               # dev/tools/peakrdl/venv (created here)
ZIP_FILE = os.path.join(PEAKRDL_DIR, "peakrdl_repos.zip")  # repos archive: made by makezip, used by mode zip

# GitHub organization that hosts the peakrdl repos
GITHUB_URL = "https://github.com/SystemRDL/"

# repos that are hosted somewhere else than GITHUB_URL (repo name -> base URL)
REPO_URLS = {
    "PeakRDL-python": "https://github.com/krcb197/",   # third-party exporter, not in the SystemRDL organization
    "PeakRDL-docx":   "https://github.com/nijmeijer/", # third-party exporter, not in the SystemRDL organization
    "peakrdl-pdflight": "https://github.com/wolfy-42/",  # our own exporter
}

# GitHub repos to clone into dev/tools/peakrdl, each with the revision to check out: a release
# tag, or a full 40-character commit hash for a repo without tags (the latest compliant
# revision, per the table above)
REPOS = [
    ("systemrdl-compiler", "v1.33.0"),   # SystemRDL parser/compiler everything else builds on
    ("PeakRDL-regblock",   "v1.3.1"),    # exporter: RTL register block
    ("PeakRDL-html",       "v2.12.2"),   # exporter: HTML documentation
    ("PeakRDL-uvm",        "v2.4.0"),    # exporter: UVM register model
    ("PeakRDL-cheader",    "v1.1.0"),    # exporter: C header
    ("PeakRDL-python",     "4.0.0"),     # exporter: Python register access package (tag has no "v")
    ("PeakRDL",            "v1.5.0"),    # holds peakrdl-cli (and the unused meta-package); no setup file of its own
    ("PeakRDL-Markdown",   "v1.0.3"),    # exporter: Markdown documentation
    ("PeakRDL-docx",       "f92b5a0717b5af404477e6cb4d98d9120eb6b9b1"),  # exporter: Word (.docx) documentation; no tags, commit = PyPI 0.4.7
    ("peakrdl-pdflight",   "v0.1.1"),    # exporter: PDF documentation (our own)
]

# folders to pip-install, in dependency order (compiler first, then the exporters, the cli, and
# the exporters that need the cli) so that pip finds each dependency already installed from the
# local folder instead of downloading a separate copy from PyPI.
INSTALL = [
    "systemrdl-compiler",
    "PeakRDL-regblock",
    "PeakRDL-html",
    "PeakRDL-uvm",
    "PeakRDL-cheader",
    "PeakRDL-python",
    "PeakRDL/peakrdl-cli",  # the "peakrdl" command line tool that loads the exporters
    "PeakRDL-Markdown",     # needs peakrdl-cli >= 1.5.0
    "PeakRDL-docx",         # installed without its declared dependencies, see NO_DEPS
]

# folders installed with "pip install --no-deps", followed by the dependencies they really need.
# PeakRDL-docx declares the "peakrdl" meta-package (which would pull in PeakRDL-ipxact and
# PeakRDL-systemrdl from PyPI) but only imports systemrdl, pyquery and docx.
NO_DEPS = {
    "PeakRDL-docx": ["pyquery>=2.0.0", "python-docx>=1.1.2"],
}

# modes pip_recorded and pip_latest: packages installed from PyPI (the same set as the repos
# above; the "peakrdl" meta-package is not used, see the notes above the table).
# pip_recorded installs exactly these versions (the recorded revisions of the repos);
# pip_latest drops the "==version" and installs the newest version PyPI has on the day.
PIP_PACKAGES = [
    "systemrdl-compiler==1.33.0",
    "peakrdl-regblock==1.3.1",
    "peakrdl-html==2.12.2",
    "peakrdl-uvm==2.4.0",
    "peakrdl-cheader==1.1.0",
    "peakrdl-python==4.0.0",
    "peakrdl-cli==1.5.0",
    "peakrdl-markdown==1.0.3",
]
PIP_NO_DEPS = {
    "peakrdl-docx==0.4.7": NO_DEPS["PeakRDL-docx"],
}

# modes pip_recorded and pip_latest: packages that are not on PyPI, installed from their git
# repo instead (package name -> repo name in REPOS/REPO_URLS). pip_recorded installs the
# recorded revision from REPOS, pip_latest the newest commit of the main branch.
PIP_GIT = {
    "peakrdl-pdflight": "peakrdl-pdflight",
}

# our own exporters (folder -> package name): in modes clone, zip and local installed editable
# from their folder after the other repos. A missing folder is skipped: the package is
# uninstalled from the venv (a stale editable install would break the peakrdl command) and a
# warning is printed at the end.
OWN_REPOS = {
    "peakrdl-pdflight": "peakrdl-pdflight",   # PDF documentation (pdflight); pins reportlab==5.1.0 itself
}

# Python for the venv, provided by uv (https://github.com/astral-sh/uv). The system python3.12
# has no development headers (Python.h, package python3.12-devel), so systemrdl-compiler cannot
# build its C++ parser with it, and its fallback build then fails. uv downloads a ready-built
# Python that includes the headers, without admin rights. uv and its Python live in
# dev/tools/peakrdl/uv (gitignored); the venv itself is still a normal venv made from that Python.
UV_VERSION = "0.13.6"      # uv release, as of 2026-11-01
PYTHON_VERSION = "3.12"    # Python for the venv (uv takes the newest 3.12.x it knows)
UV_DIR = os.path.join(PEAKRDL_DIR, "uv")
UV_BIN = os.path.join(UV_DIR, "uv")
UV_URL = ("https://github.com/astral-sh/uv/releases/download/" + UV_VERSION +
          "/uv-x86_64-unknown-linux-gnu.tar.gz")
# keep uv's Pythons and download cache inside UV_DIR instead of the home folder
UV_ENV = dict(os.environ, UV_PYTHON_INSTALL_DIR=os.path.join(UV_DIR, "python"),
              UV_CACHE_DIR=os.path.join(UV_DIR, "cache"))


def run(cmd, cwd=None, env=None):
    """Print a command, then run it (in folder cwd, with environment env, if given); stop the
    script if the command fails."""
    print("+ " + ("cd " + cwd + " && " if cwd else "") + " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=cwd, env=env)


def uv_python(version):
    """Return the path of the uv-managed Python version (e.g. "3.12"), installing uv and that
    Python into UV_DIR first if they are not there yet."""
    if not os.path.isfile(UV_BIN):
        os.makedirs(UV_DIR, exist_ok=True)
        archive = os.path.join(UV_DIR, "uv.tar.gz")
        print("+ download " + UV_URL)
        urllib.request.urlretrieve(UV_URL, archive)
        with tarfile.open(archive) as tar:          # the archive holds uv-x86_64-unknown-linux-gnu/uv
            member = [m for m in tar.getmembers() if os.path.basename(m.name) == "uv"][0]
            with open(UV_BIN, "wb") as out:
                out.write(tar.extractfile(member).read())
        os.chmod(UV_BIN, 0o755)
        os.remove(archive)
    run([UV_BIN, "python", "install", version], env=UV_ENV)   # does nothing if already installed
    return subprocess.run([UV_BIN, "python", "find", "--managed-python", version],
                          stdout=subprocess.PIPE, universal_newlines=True, env=UV_ENV,
                          check=True).stdout.strip()


def find_python(requested):
    """Return the path of the --python interpreter, checked to be Python >= 3.7."""
    names = [requested]
    for name in names:
        path = shutil.which(name)       # full path if the name is found on PATH, else None
        if not path:
            continue
        # ask the interpreter itself for its version: exit code 0 only if it is >= 3.7
        ok = subprocess.run([path, "-c", "import sys; sys.exit(sys.version_info < (3, 7))"]).returncode == 0
        if ok:
            return path
    sys.exit("ERROR: no Python >= 3.7 found (tried: " + ", ".join(names) + "). Use --python <path>.")


def clone_repos():
    """Mode clone: git clone every repo that is not checked out yet, then check out its recorded
    revision (a release tag, or a commit hash for a repo without tags).

    The checkout is a detached HEAD, so the repo sits exactly on the recorded revision. An existing
    folder is not re-cloned, but is still moved to the revision; git refuses if that would overwrite
    local changes.
    """
    for repo, tag in REPOS:
        repo_dir = os.path.join(PEAKRDL_DIR, repo)
        if not os.path.isdir(repo_dir):
            run(["git", "clone", REPO_URLS.get(repo, GITHUB_URL) + repo + ".git", repo_dir])
        run(["git", "-C", repo_dir, "-c", "advice.detachedHead=false", "checkout", tag])


# text of the warning file stored in the zip next to peakrdl_versions.txt
LICENSE_WARNING = """\
WARNING: PEAKRDL-DOCX HAS NO LICENSE.

THE REPOSITORY https://github.com/nijmeijer/PeakRDL-docx (folder PeakRDL-docx in this zip)
HAS NO LICENSE FILE, AND NO LICENSE IS GIVEN ON GITHUB OR PYPI. WITHOUT A LICENSE, NO ONE
MAY COPY, CHANGE OR REDISTRIBUTE IT. IT IS INCLUDED HERE ONLY SO THAT THE TOOL INSTALL
CAN RUN WITHOUT GITHUB ACCESS. DO NOT PASS THIS ZIP ON OUTSIDE THE PROJECT.

NOTE: PeakRDL-Markdown (folder PeakRDL-Markdown) is licensed GPL-3.0-only (see its LICENSE
file); peakrdl-pdflight is Apache-2.0 OR MIT; the other repos are LGPL or MIT licensed.
"""


def make_zip():
    """Mode makezip: zip the checked-out repos into ZIP_FILE, together with peakrdl_versions.txt
    (the recorded revisions from REPOS) and LICENSE_WARNING.txt.

    Only the files git tracks in each repo, plus its .git folder, are zipped; build files the
    install leaves in the repos (compiled parser, *.egg-info, __pycache__) are left out. The repos
    are not checked against the recorded revisions. The old zip is deleted first, because zip
    adds to an existing archive. -@: read the file names from stdin; -y: symbolic links as links.
    """
    notes = {"peakrdl_versions.txt": "".join(repo + " " + rev + "\n" for repo, rev in REPOS),
             "LICENSE_WARNING.txt": LICENSE_WARNING}
    for name, text in notes.items():
        with open(os.path.join(PEAKRDL_DIR, name), "w") as f:
            f.write(text)
    names = list(notes)
    for repo, rev in REPOS:
        tracked = subprocess.run(["git", "-C", os.path.join(PEAKRDL_DIR, repo), "ls-files"],
                                 stdout=subprocess.PIPE, universal_newlines=True, check=True).stdout
        names += [repo + "/" + n for n in tracked.splitlines()]
        for folder, _, files in os.walk(os.path.join(PEAKRDL_DIR, repo, ".git")):
            names += [os.path.relpath(os.path.join(folder, n), PEAKRDL_DIR) for n in files]
    if os.path.isfile(ZIP_FILE):
        os.remove(ZIP_FILE)
    print("+ cd " + PEAKRDL_DIR + " && zip -qy " + ZIP_FILE + " -@  (" + str(len(names)) + " files)")
    subprocess.run(["zip", "-qy", ZIP_FILE, "-@"], input="\n".join(names) + "\n",
                   universal_newlines=True, cwd=PEAKRDL_DIR, check=True)
    for name in notes:
        os.remove(os.path.join(PEAKRDL_DIR, name))


def unzip_repos():
    """Mode zip: delete the repo folders, then unpack all of them clean from ZIP_FILE.

    Existing repos are never reused: local changes in them are lost. The zip is not checked
    first: if it is missing or incomplete, the repos are deleted anyway (restore with mode clone).
    """
    for repo, rev in REPOS:
        shutil.rmtree(os.path.join(PEAKRDL_DIR, repo), ignore_errors=True)
    run(["unzip", "-q", ZIP_FILE, "-x", "peakrdl_versions.txt", "LICENSE_WARNING.txt", "-d", PEAKRDL_DIR])


def main():
    parser = argparse.ArgumentParser(description="Install peakrdl from PyPI, from GitHub clones, or from a zip of the repos.")
    parser.add_argument("--mode", choices=["venv", "pip_recorded", "pip_latest", "clone", "zip", "local", "makezip"],
                        default="clone",
                        help="venv: create ./uv (uv and the Python --python-version) and an empty venv from "
                             "that Python; "
                             "pip_recorded: install the recorded versions from PyPI; pip_latest: install the newest "
                             "versions from PyPI; clone (default): clone the repos and check out the recorded "
                             "revisions; zip: install from peakrdl_repos.zip; local: install the repos already in this "
                             "folder without touching them; makezip: create peakrdl_repos.zip")
    parser.add_argument("--python-version", default=PYTHON_VERSION,
                        help="Python version for a new venv, provided by uv (default " + PYTHON_VERSION + ")")
    parser.add_argument("--python", help="Python >= 3.7 interpreter used to create the virtual environment, "
                                         "instead of the uv-managed Python (must have its development headers)")
    args = parser.parse_args()
    from_pypi = args.mode in ("pip_recorded", "pip_latest")   # True: packages from PyPI, no local repos

    # mode venv: only create the empty venv; the install modes later reuse it and add the tools
    if args.mode == "venv":
        if os.path.isdir(VENV_DIR):
            sys.exit("ERROR: " + VENV_DIR + " already exists - delete it first to create a new one.")
        python = find_python(args.python) if args.python else uv_python(args.python_version)
        run([python, "-m", "venv", VENV_DIR])
        run([os.path.join(VENV_DIR, "bin", "python"), "--version"])
        return

    # step 1: get the repos (not needed for the pip modes)
    if args.mode == "makezip":
        make_zip()
        return
    if args.mode == "clone":
        clone_repos()
    elif args.mode == "zip":
        unzip_repos()
    # mode local: nothing to do here, the repos already in this folder are installed as they are

    # step 2: create the venv from the uv-managed Python --python-version, or from --python if given
    # (skipped if the venv already exists, e.g. made by mode venv, so the tools are added to it).
    # This is the switch from the Python that launched this script (maybe 3.6) to the newer one:
    # the venv always uses the interpreter that created it.
    if not os.path.isdir(VENV_DIR):
        python = find_python(args.python) if args.python else uv_python(args.python_version)
        run([python, "-m", "venv", VENV_DIR])
    venv_python = os.path.join(VENV_DIR, "bin", "python")   # the venv's own interpreter

    # step 3: from here on everything runs through the venv's Python, not the launching one
    run([venv_python, "-m", "pip", "install", "--upgrade", "pip"])   # recent pip for editable installs
    if from_pypi:
        # modes pip_recorded / pip_latest: the cli and each exporter as released packages from
        # PyPI (not the "peakrdl" meta-package, see the notes above). pip_latest removes the
        # "==version" pins so pip takes the newest versions.
        def version(package):
            return package if args.mode == "pip_recorded" else package.split("==")[0]
        run([venv_python, "-m", "pip", "install"] + [version(p) for p in PIP_PACKAGES])
        for package, deps in PIP_NO_DEPS.items():
            run([venv_python, "-m", "pip", "install", "--no-deps", version(package)])
            run([venv_python, "-m", "pip", "install"] + deps)
        for package, repo in PIP_GIT.items():
            rev = dict(REPOS)[repo] if args.mode == "pip_recorded" else "main"
            run([venv_python, "-m", "pip", "install",
                 package + " @ git+" + REPO_URLS[repo] + repo + ".git@" + rev])
    else:
        # modes clone, zip and local: install the repo folders in this directory, editable
        for folder in INSTALL:
            if folder in NO_DEPS:
                # a repo that declares a dependency it does not need (see NO_DEPS): install it
                # without its declared dependencies, then the ones it really uses
                run([venv_python, "-m", "pip", "install", "--no-deps", "-e", os.path.join(PEAKRDL_DIR, folder)])
                run([venv_python, "-m", "pip", "install"] + NO_DEPS[folder])
            else:
                # every other repo: normal editable install, with its dependencies
                run([venv_python, "-m", "pip", "install", "-e", os.path.join(PEAKRDL_DIR, folder)])

    # modes clone, zip and local: our own exporters from their folders; a missing folder is
    # uninstalled from the venv and reported at the end
    missing = []
    for folder, package in ({} if from_pypi else OWN_REPOS).items():
        if os.path.isdir(os.path.join(PEAKRDL_DIR, folder)):
            run([venv_python, "-m", "pip", "install", "-e", os.path.join(PEAKRDL_DIR, folder)])
        else:
            run([venv_python, "-m", "pip", "uninstall", "-y", package])   # only warns if not installed
            missing.append(folder)

    # step 4: show what got installed (version, and the exporters peakrdl found). The editable
    # list shows the local folder each peakrdl package was installed from (empty in the pip modes).
    run([venv_python, "-m", "pip", "list"] + (["--editable"] if not from_pypi else []))
    run([os.path.join(VENV_DIR, "bin", "peakrdl"), "--version"])
    run([os.path.join(VENV_DIR, "bin", "peakrdl"), "--plugins"])
    print("Done! Activate with: source " + os.path.join(VENV_DIR, "bin", "activate"))
    for folder in missing:
        print("WARNING: " + folder.upper() + " NOT FOUND IN " + PEAKRDL_DIR + " - NOT INSTALLED")


if __name__ == "__main__":
    main()

# PeakRDL install

Installs the `peakrdl` command line tool and its exporters into a virtual
environment, `venv/`, in this folder. The `Makefile` runs `install_peakrdl.py`
for you.

## Quick start

```sh
cd dev/tools/peakrdl
make install_<mode>              # pick one install_* target, see below
source venv/bin/activate         # puts peakrdl on PATH
peakrdl --plugins                # check the exporters
```

You can also run `venv/bin/peakrdl` directly without activating the venv. Use
`make -C dev/tools/peakrdl <target>` to run make from another folder.

## Make commands

| Command | What it does | Needs |
|---|---|---|
| `make` | Lists the commands. Installs nothing. | – |
| `make venv` | Creates `uv/` (uv and Python 3.12) and an empty `venv/`. The `install_*` targets reuse this venv. Stops if `venv/` already exists. | Internet the first time |
| `make install_pip_recorded` | Installs the tools from PyPI at the recorded versions. Clones nothing; not editable. Quickest. | PyPI, GitHub |
| `make install_pip_latest` | Same as above, but at the newest versions on PyPI today. The set can change between installs; use it to try newer releases. | PyPI, GitHub |
| `make install_clone` | Clones all repos from GitHub, checks out the recorded revisions and installs them editable. Existing clones are reused. Use it to refresh the repos. | GitHub, PyPI |
| `make install_zip` | **Deletes the repo folders**, unpacks them clean from `peakrdl_repos.zip` and installs them editable. **Local changes in the repos are lost.** | PyPI only (no GitHub) |
| `make install_local` | Installs the repos already in this folder as they are (any branch or local patch). Use it to rebuild the venv, or to try repos you changed by hand. | PyPI |
| `make zip` | Rebuilds `peakrdl_repos.zip` from the checked-out repos. Run `make install_clone` first so each repo is on its recorded revision, then commit the zip. | – |

"Editable" means the venv runs the source in the repo folders, so changes to
the repos take effect without reinstalling.

### Options

| Variable | Default | Use |
|---|---|---|
| `PYTHON_VERSION` | `3.12` | Python version that uv provides for a new venv, e.g. `make venv PYTHON_VERSION=3.11`. |
| `PYTHON` | (uv's Python) | Use another interpreter for the venv, e.g. `make install_clone PYTHON=/path/to/python3`. It needs its development headers. |

The venv uses Python from uv because the system `python3.12` has no
development headers, so `systemrdl-compiler` cannot build its parser with it.
uv and its Python are downloaded into `uv/` (gitignored) the first time. Keep
`uv/`: the venv runs on that Python.

To rebuild the venv from scratch, delete `venv/` and run an `install_*` target
again.

## Installed tools (recorded revisions)

| Repo | Revision | Role |
|---|---|---|
| systemrdl-compiler | v1.33.0 | SystemRDL compiler |
| PeakRDL (peakrdl-cli) | v1.5.0 | `peakrdl` command line tool |
| PeakRDL-regblock | v1.3.1 | RTL register block |
| PeakRDL-html | v2.12.2 | HTML documentation |
| PeakRDL-uvm | v2.4.0 | UVM register model |
| PeakRDL-cheader | v1.1.0 | C header |
| PeakRDL-python | 4.0.0 | Python register access package |
| PeakRDL-Markdown | v1.0.3 | Markdown documentation |
| PeakRDL-docx | commit `f92b5a0` | Word (.docx) documentation |
| peakrdl-pdflight (our own) | v0.1.1 | PDF documentation |

PeakRDL-ipxact, PeakRDL-systemrdl and the `peakrdl` meta-package are left out
on purpose, because IP-XACT is not used. The revisions and the full details
are in `install_peakrdl.py`.

## Licenses

The code in this folder (`install_peakrdl.py` and the `Makefile`) is licensed
under Apache-2.0 OR MIT, at your option; see `LICENSE` and `LICENSE-APACHE`.
Each repo keeps its own license: PeakRDL-Markdown is GPL-3.0-only, and the
others are LGPL, MIT or Apache-2.0 OR MIT.

> **Warning: PeakRDL-docx has no license.** It is in `peakrdl_repos.zip` only so
> the install can run without GitHub access. **Do not pass the zip on outside
> the project.**

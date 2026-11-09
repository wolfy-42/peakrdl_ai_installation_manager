# Current State

Update this file after every significant interaction so the next session can
pick up context without re-deriving it. Read it first at the start of a
session.

## Last updated
2026-11-08

## Project scope
This project is only the git repo in this folder: `peakrdl_ai_installation_manager`
(remote `git@github.com:wolfy-42/peakrdl_ai_installation_manager.git`, public).
It is checked out into the `dev/tools/peakrdl` folder of an FPGA project. The
upper-level (FPGA project) repo is not part of this project and is irrelevant
here: do not read, change or commit it from this project.

## Branch
`main`, tracking `origin/main`.

## Status
Repo created on 2026-11-03 and pushed; everything is committed and pushed.
Contents:
- `Makefile`, `install_peakrdl.py`: install peakrdl into `./venv` (see `README.md`).
- `peakrdl_repos.zip`: all peakrdl repos with their `.git` folders, input for
  `make install_zip`. Pushed to the public repo by user's decision, although it
  contains PeakRDL-docx (no license) and its own warning says not to share it.
- `README.md`: short, centred on the `make` commands; the quick start begins
  with the `git clone` into `dev/tools/peakrdl`.
- `LICENSE` (dual note + MIT, "Copyright (c) 2026 wolfy-42") and
  `LICENSE-APACHE`: Apache-2.0 OR MIT for the code in this folder only, not the
  repos in the subfolders.
- `.gitignore`: repo folders, `venv/`, `uv/`, `__pycache__/`, make zip temp files.
- AI scaffold: `CLAUDE.md`, `rules.md` (8 general rules), `current_state.md`,
  `open_items.md` (no items).

## In-progress work
(none)

## Notes for next session
(none)

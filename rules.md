# Project Rules

1. **Before changing any file, read its current contents first, and keep a copy of the old revision before applying changes.** Never edit blind or overwrite without a backup of what was there. For a git-tracked file, a committed state already serves as that backup; for anything else (uncommitted work, generated/scratch files), save a copy of the old version before modifying it.

2. **All rules for this project are stored in `rules.md` as a numbered list.** Do not put rules elsewhere (README.md, CLAUDE.md, comments, etc.) — add new ones here, keep the numbering sequential.

3. **Every conflict, open question, pending decision, or missing piece of information is tracked in `open_items.md`**, numbered sequentially as `OI.<group>.<item>` (e.g. `OI.1.1`). When an item is resolved, delete its entry entirely — do not just mark it done.

4. **Before executing a compile/build, ask the user to confirm `open_items.md` has no remaining open items.** Do not launch a build while open items are outstanding without explicit user confirmation to proceed anyway.

5. **Always re-read a file right before changing it, never rely on an earlier in-conversation read.** The user may edit files directly outside the AI interface (IDE, other tools) between turns; a stale in-context copy can silently overwrite those edits. This is in addition to rule 1 — re-read for freshness even if the file was already read earlier in the session.

6. **Save the current state to `current_state.md` whenever the interface has been idle for 15 minutes.** Do not wait for the next significant action: record the status, in-progress work, and notes for the next session so nothing is lost if the session ends or the context resets. Following rule 5, re-read `current_state.md` before updating it.

7. **Use as few Bash commands as possible.** Prefer the dedicated Read, Edit, Write and search tools for reading, changing and finding files. Use Bash only when no dedicated tool can do the job, and combine related steps into one command instead of running many small ones.

8. **Never assume — always ask.** When anything is unclear, ambiguous or not specified (intent, scope, names, paths, values, versions, behaviour, which option to pick), ask the user before acting instead of choosing a default. This includes details that go beyond what was literally asked. If the question cannot be answered right away, record it in `open_items.md` (rule 3) and do not act on a guess.

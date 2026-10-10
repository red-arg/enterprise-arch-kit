---
name: install
description: One-time setup that gets this project ready for a non-technical builder - checks the workspace, prepares automatic saving, records who owns the project, and explains how to start. Run only when the builder explicitly invokes it.
disable-model-invocation: true
---

# Install — get ready to build

The person running this is probably not a software engineer. Do the setup
work yourself, quietly, and talk to them only in plain, friendly language.
No commands, file names, version numbers or jargon in what you say to them.
It's safe to run more than once: skip anything that's already done.

## 1. Say hello

One short line, e.g. "Hi! I'll get everything ready — this takes a minute."

## 2. Check the workspace (silently)

Run these checks yourself; don't narrate them.

1. **The kit is present.** The `enterprise-standards` skill and the
   architecture agents (`solution_designer`, `architecture_reviewer`,
   `readability_reviewer`, `stack_guardian`, `handoff_scribe`) are available.
   If something is missing, tell the builder in one sentence that the project
   setup is incomplete and they should ask whoever gave them the project for
   a fresh copy — then stop.
2. **Saving (git).**
   - Not a git repository → `git init -b main`.
   - No `user.name` / `user.email` configured → you'll ask in step 3.
3. **Tools to run apps.** Check `node --version` (needs 20+),
   `python3 --version` (needs 3.11+) and `java -version` (21+). Node.js is the
   one most projects need. Note anything missing for step 5; don't install
   system software yourself.
4. **Spec Kit.** If `.specify/` exists, check `.specify/memory/constitution.md`
   starts with "# Project Constitution" (the enterprise one). If Spec Kit
   isn't set up, that's fine — skip it silently.
5. **Standards.** If `enterprise-standards` references still contain
   `TODO(architecture-team)` placeholders, remember to record that in the
   handoff (step 4). Don't mention it to the builder.

## 3. Ask who they are (one message)

Ask only what's missing, in one friendly message, for example:

> Before we start: what's your name and which team are you in? (So I can
> note who owns this project.)

If git has no identity, add: "…and which email should I put on your saved
work?" In GitHub Codespaces the identity is usually already set — don't ask
for it then.

Use the AskUserQuestion tool only if it fits naturally; a plain question is
fine.

## 4. Record and save (silently)

1. Configure git identity for this repository if it was missing
   (`git config user.name` / `user.email`).
2. Create `docs/production-handoff.md` from the `production-handoff` skill's
   template if it doesn't exist. Fill §1 *Business owner* and §2 *Ownership
   (Q8)* as **Confirmed** with their name and team; leave everything else for
   later. If the standards still contain placeholders, add to §9: "Enterprise
   standards in this kit are still illustrative placeholders — owner:
   Architecture". Add one change-log line.
3. If `README.md` is missing or is the starter's welcome page, leave it as is.
4. Commit everything with the message `Set up project` (skip if nothing
   changed). Don't push.

## 5. Tell them they're ready

One short, warm message. Use their first name. Include:

- That they can now just describe what they want, in their own words.
- Two or three example requests that fit their team, e.g. for HR:
  "Make a simple app where my team can request leave and I can approve it",
  "Build a dashboard showing how many requests we get each week",
  "Create a form for new joiners to submit their details".
- That you'll ask a few simple questions when needed and save their work as
  you go.
- **Only if a tool from step 2.3 is missing:** one plain sentence, e.g.
  "To run apps on this computer you'll need Node.js — the easiest option is
  to open this project in GitHub Codespaces, where everything is ready, or
  ask IT to install Node.js."

Don't list what you checked or configured. Don't mention agents, skills,
standards, Spec Kit, git or files.

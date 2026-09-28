# Agent guide

Instructions for AI agents operating on or with this repository. Humans: see [INSTALL.md](INSTALL.md).

## What this repo is
A **Claude Code plugin marketplace** (`ddeepak-marketplace`). The manifest is
`.claude-plugin/marketplace.json`; each plugin lives under `plugins/<name>/` with a
`.claude-plugin/plugin.json` and its `skills/`, `commands/`, `agents/`, and/or `hooks/`.

## Current plugins
- **`k1-workpaper-builder`** — turns Schedule K-1 (Form 1065 & 1120-S) PDF packages into a verified,
  multi-sheet Excel workpaper. Skill: `plugins/k1-workpaper-builder/skills/k1-workpaper-builder/SKILL.md`.
  Command: `/k1-workpaper <folder>`.

## How to use a skill here
1. **If installed as a plugin:** invoke via the Skill tool using the name shown in your session's
   available-skills list — plugin skills appear as `<plugin>:<skill>` (e.g.
   `k1-workpaper-builder:k1-workpaper-builder`). Use the exact listed name; do not guess.
2. **If not installed:** the skills are self-contained. Read the skill's `SKILL.md`, `pip3 install
   pymupdf openpyxl`, and run the scripts in its `scripts/` directory directly. See INSTALL.md → Part B.

## How to add a plugin to this marketplace
1. Create `plugins/<new-plugin>/.claude-plugin/plugin.json` (`name`, `version`, `description`).
2. Add `skills/<skill>/SKILL.md` (YAML frontmatter with `name` + a trigger `description`), and/or
   `commands/*.md`, `agents/*.md`, `hooks/`.
3. Append an entry to `plugins` in `.claude-plugin/marketplace.json` with `name`, `source`
   (relative path), `description`, and `version`.
4. Validate JSON, keep the skill client-agnostic (no real PII/financial data in examples), and commit.

## Guardrails
- Never commit client data: `.gitignore` excludes `*.pdf`, `*.xlsx`, `data/`, and `_k1_img/`.
- Skill examples must use fictional values.
- Preserve the render→read + tie-out method in the K-1 skill; it is the source of its accuracy.

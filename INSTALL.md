# Installing & Using this Marketplace

This guide covers installing the marketplace, its plugins, and their **skills** and **commands** —
written for both **humans** (using Claude Code interactively) and **agents / automation** (headless
sessions, CI, or other frameworks).

- Repository (git URL): **`https://github.com/deepthip47/dd-toolbox.git`**
- Marketplace name: **`dd-toolbox`** (comes from the manifest, so it stays the same even if you use a fork)
- Plugin: **`k1-workpaper-builder`** (provides the `k1-workpaper-builder` skill and the `/k1-workpaper` command)

---

## Prerequisites

| Requirement | Why | Check |
| ----------- | --- | ----- |
| Claude Code (recent version) | plugin/marketplace support | `claude --version` |
| Git | to add a remote or GitHub marketplace | `git --version` |
| Python 3.9+ and `pip3` | the K-1 plugin's scripts | `python3 --version` |
| `pymupdf`, `openpyxl` | PDF rendering + Excel output | auto-installed by the skill on first use, or `pip3 install pymupdf openpyxl` |

---

## Part A — For humans (Claude Code, interactive)

### 1. Add the marketplace
Type this **at the Claude Code prompt** — not in your terminal shell (slash commands only work
inside Claude Code):

```text
/plugin marketplace add https://github.com/deepthip47/dd-toolbox.git
```

Claude Code will ask you to **trust** the marketplace before it loads — review and confirm.

Other sources `/plugin marketplace add` accepts, if you aren't using the repo above:

```text
/plugin marketplace add https://github.com/<your-account>/dd-toolbox.git   # your own fork
/plugin marketplace add git@github.com:<your-account>/dd-toolbox.git       # SSH remote
/plugin marketplace add /path/to/your/clone/of/dd-toolbox                  # local clone (development)
```

### 2. Install the plugin (this also installs its skills + commands)
```text
/plugin install k1-workpaper-builder@dd-toolbox
```
Or browse interactively: run **`/plugin`** → **Marketplaces** → pick `dd-toolbox` →
select `k1-workpaper-builder` → **Install**. Installing a plugin automatically registers everything
it bundles — its `skills/`, `commands/`, `agents/`, and `hooks/`. You do **not** install skills
separately.

### 3. Verify it loaded
- **`/plugin`** → the plugin shows as **enabled**.
- Type **`/`** (or `/help`) → the **`/k1-workpaper`** command appears.
- **Skill:** the `k1-workpaper-builder` skill is now active. It **auto-triggers** when you ask for
  K-1 work (see step 4) — you don't call skills by hand. The `/plugin` detail view lists the skills
  a plugin provides.
- If anything is missing, **restart Claude Code** (or reload) and re-check `/plugin`.

### 4. Use it
- **Natural language (skill auto-triggers):**
  > "Build a K-1 workpaper from the Schedule K-1 PDFs in `~/Downloads/AcmeClient`."
- **Slash command (explicit):**
  ```text
  /k1-workpaper ~/Downloads/AcmeClient
  ```

### 5. Update to the latest version
```text
/plugin marketplace update dd-toolbox
```
Then, if prompted, reinstall/re-enable the plugin.

### 6. Uninstall / remove
```text
/plugin uninstall k1-workpaper-builder@dd-toolbox
/plugin marketplace remove dd-toolbox
```

### 7. Team-wide / project auto-load (optional)
To make the marketplace + plugin load automatically for everyone who opens a repo, commit a
`.claude/settings.json`. Claude Code reads project settings on startup. A representative shape:

```jsonc
{
  // register the marketplace so teammates don't have to add it manually
  "extraKnownMarketplaces": {
    "dd-toolbox": {
      "source": {
        "source": "git",
        "url": "https://github.com/deepthip47/dd-toolbox.git"
      }
    }
  },
  // enable the plugin for everyone on this project
  "enabledPlugins": { "k1-workpaper-builder@dd-toolbox": true }
}
```

> The exact settings keys can vary by Claude Code version. If in doubt, use the `/plugin` flow in
> steps 1–2 (always supported) and confirm the current schema in the Claude Code docs.

---

## Part B — For agents & automation

There are three ways an agent can use this, depending on whether the plugin runtime is available.

### Case 1 — Plugin already installed in the Claude Code session
- **Let the skill trigger itself.** When the user's request matches the skill's `description`
  (building a spreadsheet/workpaper from Schedule K-1 PDFs), the harness surfaces the skill and you
  invoke it via the **Skill tool**. Plugin skills are listed in the session's available-skills as
  **`<plugin>:<skill>`** — here `k1-workpaper-builder:k1-workpaper-builder`. Use the exact name
  shown in your environment's skill listing; don't guess.
- **Or run the command:** `/k1-workpaper <folder>`.
- Once invoked, follow `SKILL.md` end to end.

### Case 2 — No plugin runtime (headless `claude -p`, CI, or a non-Claude agent)
The skill is **self-contained**; the bundled scripts are plain Python and work standalone:

```bash
git clone https://github.com/deepthip47/dd-toolbox.git
cd dd-toolbox
pip3 install pymupdf openpyxl

SKILL=plugins/k1-workpaper-builder/skills/k1-workpaper-builder

# 1. Inventory: form-face page + 1065/1120-S per file
python3 "$SKILL/scripts/classify.py" /path/to/k1-pdfs

# 2. Render a form face to an image to read box values reliably
python3 "$SKILL/scripts/render_pdf.py" "/path/to/one.pdf" 2      # -> prints a PNG path

# 3. Read the statements/footnotes text (add --shift N if the text layer is encoded)
python3 "$SKILL/scripts/dump_pdf_text.py" "/path/to/one.pdf" all

# 4. After writing one JSON per K-1 (see references/extraction-schema.md), compile:
python3 "$SKILL/scripts/build_workbook.py" --data /path/to/data \
        --out /path/to/Client_K1_Summary.xlsx --title "Client — 2025 K-1 Summary"
```
Read `SKILL.md` for the method and `references/extraction-schema.md` for the JSON shape.

### Case 3 — Install a skill/command WITHOUT the marketplace (personal or project dirs)
Claude Code also loads skills and commands from well-known folders, so you can drop them in directly:

```bash
# Personal (all your projects):
cp -R plugins/k1-workpaper-builder/skills/k1-workpaper-builder ~/.claude/skills/
cp    plugins/k1-workpaper-builder/commands/k1-workpaper.md      ~/.claude/commands/

# Project-scoped (checked into a specific repo):
mkdir -p .claude/skills .claude/commands
cp -R plugins/k1-workpaper-builder/skills/k1-workpaper-builder .claude/skills/
cp    plugins/k1-workpaper-builder/commands/k1-workpaper.md      .claude/commands/
```
The skill then appears as `k1-workpaper-builder` (no plugin namespace) and the `/k1-workpaper`
command becomes available after a reload.

---

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| "Marketplace not found" / nothing happens on add | Make sure you typed it **at the Claude Code prompt**, not in your terminal. Use the explicit git URL (`https://github.com/deepthip47/dd-toolbox.git`), and confirm the repo is reachable for you: `git ls-remote https://github.com/deepthip47/dd-toolbox.git`. |
| Add fails behind a proxy/SSO or on a private fork | Use an SSH URL (`git@github.com:<account>/dd-toolbox.git`) with a working key, or `git clone` it and add the local path. |
| Plugin installed but `/k1-workpaper` missing | Restart/reload Claude Code; run `/plugin` and confirm the plugin is **enabled**. |
| Skill never triggers | It triggers on K-1 → spreadsheet/workpaper requests. Force it with `/k1-workpaper <folder>`, or reference the skill by the name shown in your skills list. |
| `ModuleNotFoundError: fitz` / `openpyxl` | `pip3 install pymupdf openpyxl` (ensure the same `python3` that Claude runs). |
| Statement text is garbled | Encoded text layer — add `--shift N` to `dump_pdf_text.py` (commonly `--shift 2`). The rendered image always reads correctly. |
| Form face isn't on page 1 | Cover letters / K-3 / state K-1s can precede it. Trust `classify.py`'s detected page, or render adjacent pages. |

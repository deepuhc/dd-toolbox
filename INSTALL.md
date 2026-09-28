# Installing & Using this Marketplace

This guide covers installing the marketplace, its plugins, and their **skills** and **commands** —
written for both **humans** (using Claude Code interactively) and **agents / automation** (headless
sessions, CI, or other frameworks). Wherever `<owner>` appears, substitute your GitHub username.

- Marketplace name: **`ddeepak-marketplace`**
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
Run one of these inside Claude Code (type it at the prompt). `/plugin marketplace add` accepts a
GitHub `owner/repo`, a full git URL, or a local path:

```text
/plugin marketplace add <owner>/claude-plugin-marketplace        # published GitHub repo
/plugin marketplace add https://github.com/<owner>/claude-plugin-marketplace.git
/plugin marketplace add /Users/ddeepak/claude-plugin-marketplace # local clone (development)
```

Claude Code will ask you to **trust** the marketplace before it loads — review and confirm.

### 2. Install the plugin (this also installs its skills + commands)
```text
/plugin install k1-workpaper-builder@ddeepak-marketplace
```
Or browse interactively: run **`/plugin`** → **Marketplaces** → pick `ddeepak-marketplace` →
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
/plugin marketplace update ddeepak-marketplace
```
Then, if prompted, reinstall/re-enable the plugin.

### 6. Uninstall / remove
```text
/plugin uninstall k1-workpaper-builder@ddeepak-marketplace
/plugin marketplace remove ddeepak-marketplace
```

### 7. Team-wide / project auto-load (optional)
To make the marketplace + plugin load automatically for everyone who opens a repo, commit a
`.claude/settings.json`. Claude Code reads project settings on startup. A representative shape:

```jsonc
{
  // register the marketplace so teammates don't have to add it manually
  "extraKnownMarketplaces": {
    "ddeepak-marketplace": {
      "source": { "source": "github", "repo": "<owner>/claude-plugin-marketplace" }
    }
  },
  // enable the plugin for everyone on this project
  "enabledPlugins": { "k1-workpaper-builder@ddeepak-marketplace": true }
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
git clone https://github.com/<owner>/claude-plugin-marketplace
cd claude-plugin-marketplace
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
| "Marketplace not found" on add | Repo must be public (or you must have access). Try the full `https://…​.git` URL, or add a local clone by path. |
| Plugin installed but `/k1-workpaper` missing | Restart/reload Claude Code; run `/plugin` and confirm the plugin is **enabled**. |
| Skill never triggers | It triggers on K-1 → spreadsheet/workpaper requests. Force it with `/k1-workpaper <folder>`, or reference the skill by the name shown in your skills list. |
| `ModuleNotFoundError: fitz` / `openpyxl` | `pip3 install pymupdf openpyxl` (ensure the same `python3` that Claude runs). |
| Statement text is garbled | Encoded text layer — add `--shift N` to `dump_pdf_text.py` (commonly `--shift 2`). The rendered image always reads correctly. |
| Form face isn't on page 1 | Cover letters / K-3 / state K-1s can precede it. Trust `classify.py`'s detected page, or render adjacent pages. |

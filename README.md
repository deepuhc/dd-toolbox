# dd-toolbox

A personal [Claude Code](https://claude.com/claude-code) **plugin marketplace** — a place to host
skills and plugins so you (and anyone you share it with) can install them on demand.

## Install this marketplace

**Full, step-by-step instructions for both humans and agents are in [INSTALL.md](INSTALL.md).**
Agents should also read [AGENTS.md](AGENTS.md). The short version, in Claude Code:

```text
/plugin marketplace add deepthip47/dd-toolbox
/plugin install k1-workpaper-builder@dd-toolbox
```

Installing the plugin automatically registers its **skills and commands** — there is no separate
skill-install step. Confirm with `/plugin` and by typing `/` to see the `/k1-workpaper` command;
restart/reload Claude Code if it doesn't appear immediately.

During development you can add it from a local clone instead:

```text
/plugin marketplace add /Users/ddeepak/dd-toolbox
```

The bundled scripts are also usable **standalone** (no plugin runtime) — see INSTALL.md → Part B.

## Plugins in this marketplace

| Plugin | What it does |
| ------ | ------------ |
| **k1-workpaper-builder** | Extracts Schedule K-1 (Form 1065 & 1120-S) tax packages into a verified, multi-sheet Excel workpaper — every Part III box with per-code statement detail, capital accounts, liabilities, tie-out checks, and a state income/withholding/composite summary. Provides the `/k1-workpaper` command and an auto-triggering skill. |

## Repository layout

```
.
├── .claude-plugin/
│   └── marketplace.json          # marketplace manifest (lists all plugins)
├── plugins/
│   └── k1-workpaper-builder/
│       ├── .claude-plugin/
│       │   └── plugin.json        # plugin manifest
│       ├── commands/              # slash commands (/k1-workpaper)
│       │   └── k1-workpaper.md
│       └── skills/                # auto-discovered agent skills
│           └── k1-workpaper-builder/
│               ├── SKILL.md
│               ├── scripts/       # bundled Python helpers
│               └── references/    # schema + prompt template (loaded on demand)
└── README.md
```

## Adding a new plugin

1. Create `plugins/<your-plugin>/.claude-plugin/plugin.json`.
2. Add `skills/`, `commands/`, `agents/`, or `hooks/` under the plugin directory.
3. Append an entry to `plugins` in `.claude-plugin/marketplace.json`.
4. Commit and push. Consumers run `/plugin marketplace update dd-toolbox` to pull it.

## Requirements

The `k1-workpaper-builder` plugin uses Python 3 with `pymupdf` and `openpyxl`; the skill installs
them on first use if missing.

## License

MIT — see [LICENSE](LICENSE).

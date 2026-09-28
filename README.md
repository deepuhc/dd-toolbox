# ddeepak-marketplace

A personal [Claude Code](https://claude.com/claude-code) **plugin marketplace** — a place to host
skills and plugins so you (and anyone you share it with) can install them on demand.

## Install this marketplace

In Claude Code:

```
/plugin marketplace add <your-github-username>/claude-plugin-marketplace
/plugin install k1-workpaper-builder@ddeepak-marketplace
```

You can also add it from a local clone during development:

```
/plugin marketplace add /Users/ddeepak/claude-plugin-marketplace
```

Then restart Claude Code (or reload plugins) and the plugin's skills and commands become available.

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
4. Commit and push. Consumers run `/plugin marketplace update ddeepak-marketplace` to pull it.

## Requirements

The `k1-workpaper-builder` plugin uses Python 3 with `pymupdf` and `openpyxl`; the skill installs
them on first use if missing.

## License

MIT — see [LICENSE](LICENSE).

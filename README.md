# dd-toolbox

A personal [Claude Code](https://claude.com/claude-code) **plugin marketplace** — a place to host
skills and plugins so you (and anyone you share it with) can install them on demand.

## Install this marketplace

**Full, step-by-step instructions for both humans and agents are in [INSTALL.md](INSTALL.md).**
Agents should also read [AGENTS.md](AGENTS.md). The short version, in Claude Code:

```text
/plugin marketplace add https://github.com/deepthip47/dd-toolbox.git
/plugin install k1-workpaper-builder@dd-toolbox
/plugin install 401k-wire-transfer-testing@dd-toolbox
```

Type those at the Claude Code prompt (not in your terminal shell). Claude Code will ask you to
**trust** the marketplace — confirm it. Installing the plugin automatically registers its **skills
and commands** — there is no separate skill-install step. Confirm with `/plugin` and by typing `/`
to see the `/k1-workpaper` command; restart/reload Claude Code if it doesn't appear immediately.

Working from your own fork or clone? Use that repository's git URL instead — everything else is
identical, because the marketplace name comes from the manifest, not from the URL:

```text
/plugin marketplace add https://github.com/<your-account>/dd-toolbox.git
```

The bundled scripts are also usable **standalone** (no plugin runtime) — see INSTALL.md → Part B.

## Plugins in this marketplace

| Plugin | What it does |
| ------ | ------------ |
| **k1-workpaper-builder** | Extracts Schedule K-1 (Form 1065 & 1120-S) tax packages into a verified, multi-sheet Excel workpaper — every Part III box with per-code statement detail, capital accounts, liabilities, tie-out checks, and a state income/withholding/composite summary. Provides the `/k1-workpaper` command and an auto-triggering skill. |
| **401k-wire-transfer-testing** | 401(k) plan audit WP 5220 wire transfer / timely remittance testing — matches every payroll check date's 401(k), Roth, loan and employer match withholdings to the recordkeeper's contribution report, computes business days to funding, and shows over/(under) funding. Works with any payroll provider and recordkeeper. Provides the `/5220` command and an auto-triggering skill. |

## Repository layout

```
.
├── .claude-plugin/
│   └── marketplace.json          # marketplace manifest (lists all plugins)
├── plugins/
│   ├── k1-workpaper-builder/
│       ├── .claude-plugin/
│       │   └── plugin.json        # plugin manifest
│       ├── commands/              # slash commands (/k1-workpaper)
│       │   └── k1-workpaper.md
│       └── skills/                # auto-discovered agent skills
│           └── k1-workpaper-builder/
│               ├── SKILL.md
│               ├── scripts/       # bundled Python helpers
│               └── references/    # schema + prompt template (loaded on demand)
│   └── 401k-wire-transfer-testing/
│       ├── .claude-plugin/plugin.json
│       ├── commands/5220.md       # /5220
│       └── skills/401k-wire-transfer-testing/SKILL.md
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

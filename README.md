## Agent Skills (`dccakes-skills`)

Personal Claude Code skills for working with data contracts and related tooling.

## Skills

| Skill | Description |
|-------|-------------|
| `odcs-contract` | Create, validate, and maintain [ODCS](https://github.com/bitol-io/open-data-contract-standard) v3.1.0 data contracts |

## Installation

### Option 1: Install via marketplace (recommended)


```text
/plugin marketplace add dccakes/agent-skills-marketplace
/plugin install dccakes-skills@odcs-contract
```

### Option 2: As a local plugin

Run Claude Code with the `--plugin-dir` flag pointing to this repo:

```bash
claude --plugin-dir /path/to/agent-skills
```

Skills will be namespaced as `dccakes-skills:odcs-contract`.

### Option 3: Copy to your skills directory

Copy individual skills into your personal or project skills folder:

```bash
# Personal (available in all projects)
cp -r skills/odcs-contract ~/.claude/skills/

# Project-specific
cp -r skills/odcs-contract .claude/skills/
```

### Option 4: Symlink

```bash
ln -s /path/to/agent-skills/skills/odcs-contract ~/.claude/skills/odcs-contract
```

## Prerequisites

The `odcs-contract` skill includes Python scripts that require:

```bash
pip install pyyaml jsonschema
```

## What's Included

### odcs-contract

- **SKILL.md** - Skill definition with complete ODCS v3.1.0 reference
- **TESTS.md** - 50+ test scenarios for skill validation
- **references/** - Detailed guides for quality rules, relationships, and server types
- **scripts/**
  - `new_contract.py` - Generate new contract scaffolds
  - `validate_contract.py` - Validate contracts against the ODCS JSON schema (auto-downloads from GitHub)

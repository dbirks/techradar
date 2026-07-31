# ty

Documentation: https://docs.astral.sh/ty/

GitHub: https://github.com/astral-sh/ty

Tech Radar: https://www.thoughtworks.com/en-us/radar/tools/ty

**Assessment:** Assess (April 2026, Volume 34)

`ty` is a static type checker and language server for Python, written in Rust by Astral. Static type checking is a form of static analysis: it examines Python code without running it and reports mismatches involving type annotations, inferred types, function calls, imports, attributes, and related typing rules.

## What does it replace?

`ty` occupies the same role as tools such as:

- [mypy](https://www.mypy-lang.org/)
- [Pyright](https://microsoft.github.io/pyright/) and [basedpyright](https://docs.basedpyright.com/)
- [Pyre](https://pyre-check.org/)
- [pytype](https://google.github.io/pytype/)
- [Pyrefly](https://pyrefly.org/)
- [Zuban](https://zubanls.com/)

The most direct comparison is with **mypy and Pyright**; Astral provides a migration guide specifically for those two:

https://docs.astral.sh/ty/coming-from-mypy-or-pyright/

This is not necessarily a drop-in replacement. Projects may need to translate rule names, suppression comments, severity settings, and configuration, and `ty` is currently beta software.

`ty` does **not** replace a formatter or a full linter. Use Ruff separately for those jobs:

```bash
uvx ruff check .
uvx ruff format .
```

## Common commands

Run the type checker against the current project:

```bash
uvx ty check
```

Check particular paths:

```bash
uvx ty check src tests
uvx ty check path/to/file.py
```

Recheck incrementally as files change:

```bash
uvx ty check --watch
```

Apply fixes that `ty` knows how to make:

```bash
uvx ty check --fix
```

`--fix` applies available type-checking fixes; it is **not** a formatting command.

Show concise, one-diagnostic-per-line output:

```bash
uvx ty check --output-format concise
```

Show GitHub Actions workflow annotations:

```bash
uvx ty check --output-format github
```

The output format can also be selected through an environment variable:

```bash
TY_OUTPUT_FORMAT=github uvx ty check
```

Other supported diagnostic formats are `full` (the default), `concise`, `github`, `gitlab`, and `junit`.

## GitHub Actions

A minimal workflow can install `uv` and invoke `ty` directly. The `github` output format emits GitHub workflow commands so errors and warnings appear as file-and-line annotations in the Actions log and pull-request checks.

```yaml
name: ty

on:
  pull_request:
  push:

permissions:
  contents: read

jobs:
  type-check:
    runs-on: ubuntu-latest

    steps:
      - name: Check out the repository
        uses: actions/checkout@v7

      - name: Install uv
        uses: astral-sh/setup-uv@v8

      - name: Run ty
        run: uvx ty check --output-format github
```

For a project that pins `ty` as a development dependency, prefer the reproducible project-environment version:

```bash
uv add --dev ty
uv run ty check --output-format github
```

In CI, synchronize the locked environment before running it:

```yaml
      - name: Install project dependencies
        run: uv sync --locked --dev

      - name: Run the pinned ty version
        run: uv run ty check --output-format github
```

<!-- Additional notes, examples, and scripts will be added from the presenter's follow-up instructions. -->

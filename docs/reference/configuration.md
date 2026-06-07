# Configuration Reference

Project configuration can live in `skills.toml` or `[tool.skills]`.

If both exist, `skills.toml` wins.

## `skills.toml`

```toml
agents = ["agents"]

[install]
mode = "symlink"
```

## `pyproject.toml`

```toml
[tool.skills]
agents = ["agents"]

[tool.skills.install]
mode = "symlink"
```

## Keys

### `agents`

Default install targets.

Default:

```toml
agents = ["agents"]
```

### `install.mode`

Default target install mode.

Values:

- `symlink`
- `copy`

### `cache_dir`

Global-only directory for fetched source cache.

### `state_dir`

Global-only directory for global lock and installed state.

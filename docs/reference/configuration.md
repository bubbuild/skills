# Configuration Reference

Project configuration lives in `skills.toml`.

## `skills.toml`

```toml
agents = ["agents"]

[install]
mode = "symlink"
```

Plugins may provide extra project config sources. Those sources are read below
`skills.toml`, so local project config always has the final project-scoped
override.

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

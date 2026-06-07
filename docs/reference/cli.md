# CLI Reference

## Global Options

- `-C, --cwd PATH`: run as if started in `PATH`.
- `-y, --yes`: reserved for non-interactive workflows.

## Commands

### `skills add SOURCE`

Install skills from a local or Git source.

Options:

- `--skill NAME`: install one skill. Can be repeated.
- `--agent NAME`: install to a target. Can be repeated.
- `--global`: install into global state.
- `--copy`: copy instead of symlink.

### `skills installed`

List installed skills from the current lock file.

Options:

- `--global`: read the global lock.

### `skills use SOURCE_OR_NAME`

Render a skill prompt.

Options:

- `--skill NAME`: choose a skill when rendering directly from a source.
- `--global`: read installed skills from global state.
- `--refresh`: refresh a remote source before rendering.

### `skills update [NAME ...]`

Refresh installed skills. With no names, updates all installed skills in the
selected scope.

Options:

- `--global`: update global state.

### `skills remove NAME`

Remove installed skills from targets, canonical storage, and the lock.

Use `'*'` to remove all installed skills in the selected scope.

### `skills init [NAME]`

Create a new skill folder with `SKILL.md`.

Options:

- `--description TEXT`: frontmatter description.

### `skills list [PATH]`

List skills under a directory, skill folder, or `SKILL.md`.

### `skills parse SOURCE`

Show how a source string is parsed.

### `skills config [KEY] [VALUE]`

Inspect or update configuration.

Options:

- `--local`: use project config.
- `--delete`: delete a key.

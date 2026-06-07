# Design

`skills` has one high-level entry point: `SkillsManager`.

The dependency direction is:

```text
cli -> SkillsManager -> feature modules -> hooks/plugins
```

## Why This Shape

Applications need a library API, not only a CLI. The CLI therefore stays thin:
it parses arguments, calls `SkillsManager`, and formats results.

`SkillsManager` coordinates:

- project root discovery;
- global and project configuration;
- built-in and entry point plugins;
- install, update, remove, render, and authoring workflows.

Feature modules implement behavior behind the manager. They are internal
implementation units, not user entry points.

Hooks are the extension boundary. New agents, source formats, and config
formats should be plugins instead of core branches.

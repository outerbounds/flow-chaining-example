# Flow Chaining Example

Multi-step ML pipelines rarely fit in a single flow. This project shows how to split preprocessing and training into separate flows that trigger each other — useful when teams own different stages, when stages have different compute/dependency profiles, or when you want to rerun training without re-preprocessing.

## Architecture

```
PreprocessFlow (foreach parallel)
  → publishes ProjectEvent("start_training") with payload
  → TrainFlow receives payload as Parameters, runs training
```

A trigger app in `deployments/trigger-app/` lets you fire events from a UI for testing.

## Platform features used

- **Events**: `ProjectEvent` + `@project_trigger` for flow-to-flow communication with payload
- **Foreach**: Parallel dataset processing
- **Apps**: Trigger app deployment for manual event firing

## Flows

| Flow | Trigger | What it does |
|------|---------|-------------|
| PreprocessFlow | Manual | Splits datasets via foreach, processes in parallel, publishes `start_training` event with processed paths as payload |
| TrainFlow | `@project_trigger(event="start_training")` | Receives paths via Parameter mapping, trains model |

## CI strategy

Deploy-only (no teardown or promote). Push to main triggers deploy. Uses `--from-obproject-toml` to read platform config — no yq needed.

## Run locally

```bash
python flows/preprocess/flow.py run --datasets "path1,path2,path3"
python flows/train/flow.py run --learning_rate 0.05 --n_estimators 200
```

Event-based triggering only works when deployed — locally, run flows independently.

## Good to know

- `@project_trigger` is branch-scoped: events on branch X only trigger flows on branch X. Different from `@trigger` which is global.
- Event payload keys map to Parameter names by exact string match (`processed_paths` in payload → `processed_paths = Parameter(...)` in TrainFlow).
- Two chaining patterns exist: `@project_trigger(event=...)` passes explicit payload data. `@trigger_on_finish(flow=...)` gives access to upstream artifacts via `current.trigger.run.data`. Choose based on your data passing needs.

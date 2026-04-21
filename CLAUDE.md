# Flow Chaining Example (flow_chaining_demo)

Minimal example demonstrating two patterns for chaining flows:
`@project_trigger(event=...)` for event-based triggering with payload,
and `@trigger_on_finish(flow=...)` for direct flow completion chaining.

## Platform Features Used

- **Events**: `ProjectEvent("start_training")` published from PreprocessFlow, consumed by TrainFlow via `@project_trigger`
- **Apps**: Trigger app in `deployments/trigger-app/` for firing events from a UI

## Flows

| Flow | Trigger | Purpose |
|------|---------|---------|
| PreprocessFlow | Manual | Parallel dataset processing via `foreach`, publishes `start_training` event |
| TrainFlow | @project_trigger(start_training) | Receives event payload as Parameters, runs training |

## Key Pattern

PreprocessFlow publishes a `ProjectEvent("start_training")` with payload.
TrainFlow's `@project_trigger(event="start_training")` maps payload keys to
`Parameter` names (e.g., `processed_paths`). This is the recommended approach
over `@trigger_on_finish` when you need to pass data via event payload.

## Run Locally

```bash
cd flow-chaining-example
python flows/preprocess/flow.py run --datasets "path1,path2,path3"
python flows/train/flow.py run --learning_rate 0.05 --n_estimators 200
```

## Common Pitfalls

- Event payload values map to Parameters by name; `processed_paths` is sent as JSON string and parsed in the flow
- `@project_trigger` is branch-scoped (events only trigger flows on the same branch)
- TrainFlow cannot access upstream artifacts when triggered by event (unlike `@trigger_on_finish` which exposes `current.trigger.run.data`)
- The README describes `@trigger_on_finish` but the actual code uses `@project_trigger` -- the event-based pattern was adopted later

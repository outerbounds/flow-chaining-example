# Flow Chaining Example

Minimal example showing how to chain flows using `@trigger_on_finish`.

## Structure

```
flow-chaining-example/
  obproject.toml
  flows/
    preprocess/flow.py   # Runs first, processes datasets in parallel
    train/flow.py        # Triggered when preprocess finishes
```

## How It Works

1. **PreprocessFlow** runs with a `datasets` parameter (comma-separated paths)
2. Uses `foreach` to process each dataset in parallel
3. Stores results in `self.processed_paths` artifact
4. **TrainFlow** has `@trigger_on_finish(flow="PreprocessFlow")`
5. When PreprocessFlow completes, TrainFlow starts automatically
6. TrainFlow accesses data via `current.trigger.run.data.processed_paths`

## Testing Locally

```bash
# Test PreprocessFlow standalone
cd flows/preprocess
python flow.py run --datasets "path1,path2,path3"

# Test TrainFlow standalone (without trigger)
cd flows/train
python flow.py run --learning_rate 0.05 --n_estimators 200
```

## Deploy to Outerbounds

```bash
obproject-deploy
```

After deploy:
1. Run PreprocessFlow from UI or CLI
2. TrainFlow will trigger automatically when it finishes
3. TrainFlow parameters (learning_rate, n_estimators) use deploy-time defaults

## Passing Parameters at Runtime

TrainFlow parameters are set at **deploy time** via the flow definition defaults.
To change them per-run, either:

1. **Redeploy** with different defaults
2. **Use artifacts** instead of Parameters for runtime values:
   - PreprocessFlow stores config in an artifact
   - TrainFlow reads it via `current.trigger.run.data.config`

## Key Pattern

```python
# In TrainFlow
@trigger_on_finish(flow="PreprocessFlow")
class TrainFlow(ProjectFlow):

    @step
    def start(self):
        if current.trigger:
            # Access parent flow's artifacts
            data = current.trigger.run.data.processed_paths
```

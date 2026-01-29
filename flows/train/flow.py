"""
Train Flow: Triggered automatically when PreprocessFlow finishes.
Accesses PreprocessFlow's outputs via current.trigger.run.data
"""

from metaflow import step, Parameter, current, trigger_on_finish
from obproject import ProjectFlow, project_trigger


@project_trigger(event="start_training") # @trigger_on_finish(flow="PreprocessFlow")
class TrainFlow(ProjectFlow):
    """
    Training flow. Triggered automatically when PreprocessFlow completes.
    """

    learning_rate = Parameter("learning_rate", default=0.01, type=float)
    n_estimators = Parameter("n_estimators", default=100, type=int)

    @step
    def start(self):
        # Access data from the trigger
        if current.trigger:
            # @project_trigger provides data via event payload
            if current.trigger.event:
                payload = current.trigger.event.get("payload", {})
                self.input_paths = payload.get("processed_paths", [])
                print(f"Triggered by event, payload: {payload}")
            # @trigger_on_finish provides current.trigger.run
            elif current.trigger.run:
                self.input_paths = current.trigger.run.data.processed_paths
                print(f"Triggered by flow: {current.trigger.run.pathspec}")
            else:
                self.input_paths = []
            print(f"Input paths: {self.input_paths}")
        else:
            # Standalone run - use defaults for testing
            self.input_paths = ["test/path1_processed", "test/path2_processed"]
            print(f"Standalone run. Using test paths: {self.input_paths}")

        self.next(self.train)

    @step
    def train(self):
        """Train model using preprocessed data"""
        print(f"Training with lr={self.learning_rate}, n_estimators={self.n_estimators}")
        print(f"Using data: {self.input_paths}")
        self.model_path = "s3://bucket/models/trained_model"
        self.metrics = {"accuracy": 0.95, "f1": 0.93}
        self.next(self.end)

    @step
    def end(self):
        print(f"Training complete. Model: {self.model_path}")
        print(f"Metrics: {self.metrics}")


if __name__ == "__main__":
    TrainFlow()

"""
Preprocess Flow: Processes multiple datasets in parallel.
When finished, automatically triggers TrainFlow.
"""

from metaflow import step, Parameter, current
from obproject import ProjectFlow, ProjectEvent


class PreprocessFlow(ProjectFlow):
    """
    Preprocesses datasets. Runs multiple configs in parallel via foreach.
    """

    datasets = Parameter(
        "datasets",
        default="s3://bucket/data1,s3://bucket/data2",
        help="Comma-separated dataset paths",
    )

    @step
    def start(self):
        self.dataset_list = self.datasets.split(",")
        print(f"Processing {len(self.dataset_list)} datasets: {self.dataset_list}")
        self.next(self.preprocess, foreach="dataset_list")

    @step
    def preprocess(self):
        """Process each dataset (A1, A2, etc.)"""
        self.dataset_path = self.input
        self.output_path = f"{self.dataset_path}_processed"
        print(f"Preprocessed: {self.dataset_path} -> {self.output_path}")
        self.next(self.join)

    @step
    def join(self, inputs):
        """Merge results from parallel preprocessing"""
        self.processed_paths = [inp.output_path for inp in inputs]
        print(f"All preprocessed: {self.processed_paths}")
        self.next(self.end)

    @step
    def end(self):
        # These artifacts are accessible to TrainFlow via current.trigger.run.data
        print(f"Preprocess complete. Outputs: {self.processed_paths}")

        # Trigger TrainFlow via ProjectEvent (auto-detects project/branch)
        # Payload values map to Parameters, so send as JSON string
        import json
        pe = ProjectEvent("start_training")
        # print(f"ProjectEvent: {pe} is publishing on project {pe.project} and branch {pe.branch}.")
        pe.publish(
            payload={"processed_paths": json.dumps(self.processed_paths)}
        )
        print("Published start_training event")


if __name__ == "__main__":
    PreprocessFlow()

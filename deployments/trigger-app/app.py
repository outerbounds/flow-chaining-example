"""Minimal app to test ProjectEvent triggering a flow."""

import os
import json
import uuid
import streamlit as st
from metaflow import Flow, namespace
from metaflow.integrations import ArgoEvent

st.title("Flow Trigger Test")

project = os.environ.get("OB_PROJECT")
branch = os.environ.get("OB_BRANCH")

st.write(f"Project: {project}, Branch: {branch}")

# Get latest PreprocessFlow result
default_paths = '["s3://bucket/data1_processed", "s3://bucket/data2_processed"]'
latest_run_info = None

try:
    namespace(None)  # Search all namespaces
    flow = Flow("PreprocessFlow")
    latest_run = flow.latest_successful_run
    if latest_run and hasattr(latest_run.data, "processed_paths"):
        default_paths = json.dumps(latest_run.data.processed_paths)
        latest_run_info = f"From run {latest_run.pathspec}"
except Exception as e:
    latest_run_info = f"Could not fetch latest run: {e}"

st.subheader("Trigger TrainFlow")

if latest_run_info:
    st.caption(latest_run_info)

processed_paths = st.text_area(
    "Processed paths (JSON array)",
    value=default_paths,
    height=100
)

if st.button("Trigger TrainFlow"):
    try:
        # Validate JSON
        json.loads(processed_paths)
        event_name = f"prj.{project}.{branch}.start_training"
        event_id = str(uuid.uuid4())
        st.write(f"Publishing event: {event_name}")
        ArgoEvent(event_name).publish(payload={
            "processed_paths": processed_paths,
            "id": event_id,
        })
        st.success(f"Event published! ID: `{event_id}`")
    except json.JSONDecodeError:
        st.error("Invalid JSON format for processed_paths")

"""Minimal app to test ProjectEvent triggering a flow."""

import os
import json
import streamlit as st
from metaflow import Flow, namespace
from obproject import ProjectEvent

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
        pe = ProjectEvent("start_training", project=project, branch=branch)
        st.write(f"Publishing event: {pe.event}")
        event_id = pe.publish(payload={"processed_paths": processed_paths})
        st.success(f"Event published! ID: `{event_id}`")
    except json.JSONDecodeError:
        st.error("Invalid JSON format for processed_paths")

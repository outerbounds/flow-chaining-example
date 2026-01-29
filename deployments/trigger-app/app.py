"""Minimal app to test ProjectEvent triggering a flow."""

import streamlit as st
from obproject import ProjectEvent

st.title("Flow Trigger Test")

if st.button("Trigger PreprocessFlow"):
    ProjectEvent("start_preprocess").publish(payload={"datasets": "s3://test/a,s3://test/b"})
    st.success("Event published!")

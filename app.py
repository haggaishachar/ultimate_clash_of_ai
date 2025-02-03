import numpy as np
import streamlit as st


st.set_page_config(page_title="AI Challenge Game")
st.sidebar.title("API Keys")
openai_api_key = st.sidebar.text_input("Open AI API Key", key="openai_api_key")
vertex_api_key = st.sidebar.text_input("Vertex AI API Key", key="vertexai_api_key")


st.title("AI Models Challenge Game")
st.subheader("Mirror, Mirror on the Wall, Who's the Smartest AI of All")
st.divider()

instructions = open("instructions.txt", "r").read()
st.markdown(instructions)

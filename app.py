import streamlit as st
from challenge1 import run_game


st.set_page_config(page_title="Ultimate AI Clash")
st.sidebar.title("API Keys")
openai_api_key = st.sidebar.text_input("Open AI API Key", key="openai_api_key")
vertex_api_key = st.sidebar.text_input("Vertex AI API Key", key="vertexai_api_key")


st.title("Ultimate AI Clash")

if "game_started" not in st.session_state:
    instructions = open("instructions.txt", "r").read()
    st.markdown(instructions)

if st.button("Let the challenge begin", type="primary"):
    st.session_state["game_started"] = True
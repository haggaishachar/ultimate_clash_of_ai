import json
import os
import uuid
from random import choice

import streamlit as st
import dotenv
from challenge import run_game

dotenv.load_dotenv()

def sim_mode_container():
    st.sidebar.title("Simulation Mode")
    st.sidebar.write("View questions, answers, and scores from randomly selected past challenges.")
    if st.sidebar.button("🎲 Load a Random Challenge", type="primary"):
        challenges_ids = os.listdir('challenges')
        if len(challenges_ids) == 0:
            st.sidebar.warning("No past challenges found.")
        else:
            challenge_id = choice(challenges_ids)
            game = json.load(open(f"challenges/{challenge_id}", "r"))
            print_game(competitors=game['competitors'], messages=game['messages'], save=False)
            st.session_state['mode'] = 'simulation'


def live_mode_container():
    st.sidebar.title("Live Mode")

    openai_model = st.sidebar.text_input("ChatGPT Model:", "gpt-4o-mini")
    vertex_model = st.sidebar.text_input("Gemini Model:", "gemini-2.0-flash-exp")
    # anthropic_model = st.sidebar.text_input("Anthropic Model", "claude-3-5-haiku")
    llama_model = st.sidebar.text_input("Llama Model:", "llama-3.1-8b-instruct-maas")
    rounds = st.sidebar.number_input("Number of Rounds:", min_value=1, value=1)

    if st.sidebar.button("⚡ Start a Live Challenge", type="primary"):
        st.session_state['mode'] = 'live'

        competitors = [
            {'name': 'ChatGPT', 'model': openai_model, 'type': 'openai'},
            {'name': 'Gemini', 'model': vertex_model, 'type': 'vertexai'},
            {'name': 'Llama', 'model': llama_model, 'type': 'vertexai', 'location': "us-central1"},
        ]

        st.empty()
        messages = run_game(rounds=rounds, competitors_arr=competitors)
        print_game(competitors=competitors, messages=messages, save=True)


def print_game(competitors, messages, save):
    out = []
    for resp in messages:
        out.append(resp)
        role = resp['role']
        if role in [model['name'] for model in competitors]:
            with st.chat_message(role, avatar=f'images/{role}.png'):
                st.markdown(resp['content'])
        else:
            with st.chat_message('assistant'):
                st.markdown(resp['content'])

    if save:
        challenge_id = str(uuid.uuid4())[:8]
        challenge = {'competitors': competitors, 'messages': out, }
        with open(f"challenges/{challenge_id}.json", "w") as out:
            json.dump(challenge, out, indent=4)

st.set_page_config(page_title="Ultimate Clash of AI")
st.sidebar.image("images/logo.jpg")
st.sidebar.markdown("Developed by: [Haggai Shachar](https://www.linkedin.com/in/haggaishachar/)")
st.sidebar.divider()
sim_mode_container()
st.sidebar.divider()
live_mode_container()

if 'mode' not in st.session_state:
    with open("README.md", "r") as home:
        st.markdown(home.read())
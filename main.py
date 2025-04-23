# -*- encoding: utf-8 -*-
# @Time: 2025/04/22 18:20
# @Author: Mainak
# @Description: Video Promt Generation System
# @Email: mainak.basak101@gmail.com
# @File: main.py
# @Version: 1.0
# @Software: VSCode
# @Project: MindAI
# @Description: This is a application for generating video prompts using AI. It allows users to input a concept, generates a prompt, and provides options to edit and generate a video based on the prompt. The app also includes a history feature to track previous prompts and their edits.

import streamlit as st
import difflib
from datetime import datetime

#sessions for history purpose
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_prompt' not in st.session_state:
    st.session_state.current_prompt = ''
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

st.set_page_config(page_title="AI Video Generator", layout="wide")

#I used this to set the font and style of the sofware
st.markdown(
    """
    <link href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap' rel='stylesheet'>
    <style>
      body { font-family: 'Poppins', sans-serif; transition: background-color 0.3s, color 0.3s; }
      h1 { font-size: 2.5rem; font-weight: 600; }
      .stButton>button { border-radius: 12px; }
      .stTextArea>div>textarea { border-radius: 8px; }
      .stExpanderHeader { font-weight: 500; }
    </style>
    """,
    unsafe_allow_html=True
)

#Kept a placeholder for the API key as directed in the task
st.text_input("API Key", type="password", key="api_key", placeholder="Enter API Key for real video generation")

#I added an extra feature to set day/night mode
theme_toggle = st.checkbox("Dark Mode", value=(st.session_state.theme=='dark'))
st.session_state.theme = 'dark' if theme_toggle else 'light'

if st.session_state.theme == 'dark':
    bg_color = '#181A1B'
    text_color = '#E0E0E0'
else:
    bg_color = '#F0F4F8'
    text_color = '#121212'
st.markdown(f"""
    <style>
      body {{ background-color: {bg_color}; color: {text_color}; }}
      .main {{ background-color: {bg_color}; }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>MindAI Video Generation System</h1>", unsafe_allow_html=True)

def generate_enhanced_prompt(user_input: str) -> str:
    return f"{user_input}"


def suggest_prompt(input_text: str) -> str:
    best = (0, None)
    words = set(input_text.split())
    for rec in st.session_state.history:
        common = len(words & set(rec['edited'].split()))
        if common > best[0]: best = (common, rec['edited'])
    return best[1]


def generate_video_api(api_key: str, prompt: str) -> str:
    return f"{prompt.replace(' ', '%20')}&key={api_key}"


col1, col2 = st.columns([2,3])

if not st.session_state.current_prompt:
    concept = col1.text_area("Enter Prompt...", height=100, key="concept")
    suggestion = suggest_prompt(concept) if concept else None
    if suggestion:
        col1.markdown(f"Suggested: **{suggestion}**")
        if col1.button("Use Suggested Prompt"):
            st.session_state.current_prompt = suggestion
    if col1.button("Generate Prompt"):
        if concept.strip():
            st.session_state.current_prompt = generate_enhanced_prompt(concept.strip())

if st.session_state.current_prompt:
    new_prompt = col1.text_area(
        "Edit Generated Prompt:", value=st.session_state.current_prompt, height=100, key="edit_prompt"
    )
    if col1.button("Generate Video"):
        #diff
        diff = list(difflib.unified_diff(
            st.session_state.current_prompt.splitlines(),
            new_prompt.splitlines(),
            fromfile='generated', tofile='edited', lineterm=""
        ))
        st.session_state.history.append({
            'timestamp': datetime.now().isoformat(),
            'original': st.session_state.current_prompt,
            'edited': new_prompt,
            'diff': diff
        })
        
        if st.session_state.api_key:
            video_url = generate_video_api(st.session_state.api_key, new_prompt)
        else:
            video_url = "prompt_mock-vid.mp4"
        col2.video(video_url)
        col2.markdown(f"**Final Prompt:** {new_prompt}")
        st.session_state.current_prompt = ''

with st.expander("View Prompt History"):
    if st.session_state.history:
        for idx, rec in enumerate(reversed(st.session_state.history), start=1):
            st.markdown(f"**{idx}.** {rec['timestamp']}")
            st.write("Original:", rec['original'])
            st.write("Edited:", rec['edited'])
            if rec['diff']:
                st.code("\n".join(rec['diff']), language='diff')
            else:
                st.info("No changes recorded.")
    else:
        st.info("No history yet.")

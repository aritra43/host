import numpy as np
np.float_ = np.float64  # Patch np.float_ to avoid errors
import sys
import os
import subprocess

# Ensure pysqlite3 is installed
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3  # Override default sqlite3 with pysqlite3
except ImportError:
    print("pysqlite3 not installed. Installing now...")
    subprocess.run(["pip", "install", "pysqlite3-binary"])
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3

from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
import streamlit as st
import openai
import chromadb

# Load environment variables
load_dotenv()

# Streamlit Page Configuration
st.set_page_config(page_title="EducatorAI", layout="wide")

# Title and description
st.title("AI Educator Powered By CrewAI")
st.markdown("Please provide a text file only")

# Sidebar
with st.sidebar:
    st.header("Content Settings")
    topic = st.text_area("Enter the topic", height=68, placeholder="Enter the topic", key="text_area_1")
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])
    st.markdown("-----")
    generate_button = st.button("Generate Content", type="primary", use_container_width=True)

# Function to read file content
def read_file_content(uploaded_file):
    if uploaded_file is not None:
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)
        temp_file_path = os.path.join("temp", uploaded_file.name)
        
        # Save uploaded file
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Read file content
        with open(temp_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return content, temp_file_path
    return None, None

def generate_content(topic, uploaded_file):
    content, file_path = read_file_content(uploaded_file)

    if content:
        researcher = Agent(
            role="Senior Data Researcher",



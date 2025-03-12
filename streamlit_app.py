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
    generate_button = st.button("Generate Content", type="primary", use_container_width=True)  # ✅ Fixed issue

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
        try:
            with open(temp_file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()  # ✅ Strip to remove empty spaces
            if not content:
                raise ValueError("File is empty.")
            return content, temp_file_path
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None, None
    return None, None

# Function to generate content using CrewAI
def generate_content(topic, uploaded_file):
    if not uploaded_file:
        st.error("No file uploaded. Please upload a valid file.")
        return None, None

    content, file_path = read_file_content(uploaded_file)

    if not content:
        st.error("Uploaded file is empty or could not be read. Please upload a valid file.")
        return None, None

    researcher = Agent(
        role="Senior Data Researcher",
        goal=f"Uncover cutting-edge developments in {topic}",
        description=f"Analyze the file content and extract information related to {topic}.",
        backstory="A highly experienced data scientist with expertise in text extraction and knowledge mining.",
        verbose=True,
        memory=True,
        tools=[content],
        allow_delegation=True
    )

    reporting_analyst = Agent(
        role="Reporting Analyst",
        goal=f"Create detailed reports based on {topic} research findings",
        description="Write and format the extracted content into a structured report.",
        backstory="A meticulous report analyst with years of experience in compiling structured data into detailed reports.",
        verbose=True,
        memory=True,
        tools=[content],
        allow_delegation=True
    )

    research_task = Task(
        description=f"Analyze and extract key information about {topic}.",
        expected_output=f"A structured dataset of extracted information on {topic}.",
        agent=researcher
    )

    reporting_task = Task(
        description=f"Compile and format extracted data into a report.",
        expected_output=f"A well-organized markdown report on {topic}.",
        agent=reporting_analyst
    )

    crew = Crew(
        agents=[researcher, reporting_analyst],
        tasks=[research_task, reporting_task],
        process=Process.sequential,
        verbose=True
    )

    try:
        result = crew.kickoff(inputs={"topic": topic, "content": content})

        if not result:
            raise ValueError("CrewAI returned an empty response.")

        # Convert CrewOutput to string
        result_text = str(result)

        # Save output to a file
        output_file_path = os.path.join("temp", "report.txt")
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(result_text)

        return result_text, output_file_path
    except Exception as e:
        st.error(f"Error during content generation: {str(e)}")
        return None, None

# Main Content Area
if generate_button:
    with st.spinner("Generating Content...This may take a moment..."):
        try:
            result, output_file_path = generate_content(topic, uploaded_file)
            if result:
                st.markdown("### Generated Content")
                st.markdown(result)
                
                # Allow user to download the generated content
                with open(output_file_path, "rb") as f:
                    st.download_button(label="Download Content", data=f.read(), file_name="article.txt", mime="text/plain")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("----")
st.markdown("Built by AritraM")





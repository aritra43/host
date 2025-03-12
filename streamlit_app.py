import os
import streamlit as st
from crewai import Agent, Crew, Task, Process
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit Page Configuration
st.set_page_config(page_title="AI Educator", layout="wide")

# Title and description
st.title("AI Educator Powered By CrewAI")
st.markdown("Please provide a text file only.")

# Initialize session state
if "file_content" not in st.session_state:
    st.session_state["file_content"] = None

# Sidebar
with st.sidebar:
    st.header("Content Settings")
    topic = st.text_area("Enter the topic", height=68, placeholder="Enter the topic", key="text_area_1")

    uploaded_file = st.file_uploader("Choose a file", type=["txt"])

    if uploaded_file is not None:
        st.session_state["file_content"] = uploaded_file.getvalue().decode("utf-8").strip()

    st.markdown("-----")
    generate_button = st.button("Generate Content", type="primary", use_container_width=True)

# Function to generate content using CrewAI
def generate_content(topic):
    content = st.session_state.get("file_content", None)

    if not content:
        st.error("Unable to create the report. File content not provided.")
        return None, None

    researcher = Agent(
        role="Senior Data Researcher",
        goal=f"Extract key information on {topic}",
        description="Analyze file content and extract relevant data.",
        backstory="A skilled researcher specializing in text analysis.",
        verbose=True,
        memory=True,
        tools=[],  # No external tools needed
        allow_delegation=True
    )

    reporting_analyst = Agent(
        role="Reporting Analyst",
        goal=f"Create a structured report on {topic}",
        description="Format the extracted information into a structured document.",
        backstory="An expert in compiling detailed reports.",
        verbose=True,
        memory=True,
        tools=[],  # No external tools needed
        allow_delegation=True
    )

    research_task = Task(
        description=f"Analyze the provided content and extract key points about {topic}.",
        expected_output=f"A structured summary of {topic}.",
        agent=researcher,
        inputs={"content": content}  # ✅ Explicitly pass content to the task
    )

    reporting_task = Task(
        description=f"Compile and format extracted data into a professional report.",
        expected_output=f"A detailed markdown report on {topic}.",
        agent=reporting_analyst,
        inputs={"content": content}  # ✅ Explicitly pass content to the task
    )

    crew = Crew(
        agents=[researcher, reporting_analyst],
        tasks=[research_task, reporting_task],
        process=Process.sequential,
        verbose=True
    )

    try:
        st.write("Processing... Please wait.")
        result = crew.kickoff()  # No need for `inputs` here; tasks already receive content

        if not result:
            raise ValueError("CrewAI returned an empty response.")

        result_text = str(result)
        output_file_path = os.path.join("temp", "report.txt")
        os.makedirs("temp", exist_ok=True)

        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(result_text)

        return result_text, output_file_path
    except Exception as e:
        st.error(f"Error during content generation: {str(e)}")
        return None, None

# Main Content Area
if generate_button:
    with st.spinner("Generating Content...This may take a moment..."):
        result, output_file_path = generate_content(topic)
        if result:
            st.markdown("### Generated Content")
            st.markdown(result)

            with open(output_file_path, "rb") as f:
                st.download_button(label="Download Report", data=f.read(), file_name="report.txt", mime="text/plain")

# Footer
st.markdown("----")
st.markdown("Built by AritraM")









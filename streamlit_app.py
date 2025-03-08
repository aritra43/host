from crewai import Agent
# from tools import yt_tool
# from dotenv import load_dotenv
from crewai import LLM
import litellm
import openai
import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from crewai_tools import FileReadTool, FileWriterTool
import streamlit as st

load_dotenv()

# Title
st.set_page_config(page_title="EducatorAI", layout="wide")

# Title and description
st.title("AI Educator Powered By CrewAI")
st.markdown("Please provide a text file only")

# Sidebar
with st.sidebar:
    st.header("Content Settings")

    topic = st.text_area(
        "Enter the topic",
        height=68,
        placeholder="Enter the topic",
        key="text_area_1"
    )

    uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])

    st.markdown("-----")

    generate_button = st.button("Generate Content", type="primary", use_container_width=True)

def generate_content(topic, uploaded_file, blog="default"):
    if uploaded_file is not None:
        # Create the temp directory if it does not exist
        if not os.path.exists("temp"):
            os.makedirs("temp")

        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join("temp", uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Create a FileReadTool with the path to the uploaded file
        file_read_tool = FileReadTool(file_path=temp_file_path)

        # Create a senior blog content researcher
        researcher = Agent(
            role='Senior Data Researcher',
            goal='Uncover cutting-edge developments in {topic}',
            description='Scrape the PDF documents to extract information related to {topic}.',
            verbose=True,
            memory=True,
            backstory=(
                "You're a seasoned researcher with a knack for uncovering the latest "
                "developments in {topic}. Known for your ability to find the most relevant "
                "information and present it in a clear and concise manner from the given file."
            ),
            allow_delegation=True,
            tools=[file_read_tool]
        )

        # Create a reporting analyst agent
        reporting_analyst = Agent(
            role='Reporting Analyst',
            goal='Create detailed reports based on {topic} data analysis and research findings',
            description='Write the scraped content from the researcher and display the findings in a report format.',
            verbose=True,
            memory=True,
            backstory=(
                "You're a meticulous analyst with a keen eye for detail. You're known for "
                "your ability to turn complex data into clear and concise reports, making "
                "it easy for others to understand and act on the information you provide."
            ),
            allow_delegation=True,
            tools=[file_read_tool, FileWriterTool()]
        )

        research_task = Task(
            description=(
                "Scrape the content of the PDF and gather information about {topic}. "
                "Ensure that you extract all relevant data and details."
            ),
            expected_output='A comprehensive list of extracted information about {topic}.',
            agent=researcher,
        )

        reporting_task = Task(
            description=(
                "Write down the scraped content provided by the research specialist. "
                "Ensure the report is well-organized and detailed."
            ),
            expected_output='A detailed report based on the extracted information, formatted as markdown.',
            agent=reporting_analyst,
            output_file='report.txt'
        )

        # Crew
        crew = Crew(
            agents=[researcher, reporting_analyst],
            tasks=[research_task, reporting_task],
            process=Process.sequential,
            verbose=True,
        )

        return crew.kickoff(inputs={"topic": topic})
    else:
        st.error("Please upload a file to proceed.")
        return None

# Main content area
if generate_button:
    with st.spinner("Generating Content...This may take a moment.."):
        try:
            result = generate_content(topic, uploaded_file)
            if result:
                st.markdown("### Generated Content")
                st.markdown(result)

                # Add download button
                st.download_button(
                    label="Download Content",
                    data=result.raw,
                    file_name=f"article.txt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("----")
st.markdown("Built by AritraM")

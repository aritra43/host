__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

load_dotenv()

# Title
st.set_page_config(page_title="EducatorAI", layout="wide")

# Title and description
st.title("BRD To SRS Generator")
st.markdown("Generate an SRS from a BRD using AI agents.")
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

        business_analyst = Agent(
            role='Business Analyst',
            goal=(
            "Extracts relevant content from the given business requirements document, including "
            "Introduction, Purpose, In Scope, Out of Scope, Assumptions, References and Overview. "
            "Enhances unclear sections using the LLM and internet sources to ensure completeness "
            "before passing refined content for documentation."
            ),
            backstory=(
            "A senior business analyst with expertise in understanding business requirements and "
            "ensuring clarity in documentation."
            ),
            tools=[file_read_tool]
        )

        technical_analyst = Agent(
            role='Technical Analyst',
            goal=(
            "Analyzes the business requirements document to identify technical aspects, including "
            "Data Model, User Characteristics, Codification Schemes and Dependencies. Uses the LLM "
            "and internet to enhance unclear details before passing structured insights for documentation."
            ),
            backstory=(
            "A senior technical analyst with expertise in translating business needs into clear technical "
            "specifications."
            ),
            tools=[file_read_tool]
        )

        requirement_categorizer = Agent(
            role='Requirement Categorizer',
            goal=(
            "Classifies extracted requirements into Functional, Non-Functional, and Technical categories. "
            "Ensures clarity by refining vague or incomplete sections using the LLM and internet sources "
            "before passing structured requirements for SRS documentation."
            ),
            backstory=(
            "A senior analyst specializing in categorizing and refining requirements to ensure clarity and completeness."
            ),
            tools=[file_read_tool]
        )

        srs_writer = Agent(
            role='System Requirements Specifications Writer',
            goal=(
            "Writes a structured SRS document by incorporating the extracted and categorized requirements. "
            "Enhances the content for grammatical accuracy, professionalism, and clarity."
            ),
            backstory=(
            "A professional writer specializing in crafting well-structured and polished SRS documents."
            ),
            tools=[file_read_tool, FileWriterTool()]
        )

        srs_formatter = Agent(
            role='System Requirements Specifications Formatter',
            goal=(
            "Organizes the document with appropriate formatting, headings, and structure. Ensures that the final "
            "document is readable, structured, and includes a 'Dependencies' section which points out the dependencies "
            "on third-party APIs, database requirements, hardware constraints or system integrations and a 'Conclusion' "
            "section summarizing key insights."
            ),
            backstory=(
            "A document specialist with expertise in structuring and formatting professional reports."
            ),
            tools=[file_read_tool, FileWriterTool()]
        )

        business_analysis_task = Task(
            description=(
            "Objective:\n"
            "Extract and enhance sections from the Business Requirements Document (BRD):\n"
            "- Introduction\n"
            "- Purpose\n"
            "- Scope\n"
            "- In Scope\n"
            "- Out of Scope\n"
            "- Assumptions\n"
            "- References\n"
            "- Overview\n"
            "Enhance extracted sections with:\n"
            "- In-depth explanations\n"
            "- Real-world examples\n"
            "- Industry best practices\n"
            "- Structured details for client clarity\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n\n"
            "Guidelines:\n"
            "Introduction:\n"
            "- Provide project background, business context, and purpose.\n"
            "- Explain the need for the initiative and expected impact.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "Purpose:\n"
            "- Define document objectives and stakeholder guidance.\n"
            "- Distinguish between business and technical goals.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "Scope:\n"
            "- Explicitly outline project boundaries.\n"
            "- Include functional, non-functional, regulatory, and operational constraints.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "In Scope:\n"
            "- Detail included features, functionalities, and deliverables.\n"
            "- Provide examples and real-world implications.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "Out of Scope:\n"
            "- Extract as-is without modifications.\n"
            "- Provide context on exclusions and associated risks.\n"
            "Assumptions:\n"
            "- Extract as-is without modifications.\n"
            "- Expand on implications and potential risks if assumptions change.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "References:\n"
            "- List cited materials, frameworks, and standards.\n"
            "- Enhance with best practices and industry standards.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "Overview:\n"
            "- Summarize key takeaways in a structured format.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n\n"
            "Enhancements:\n"
            "- Ensure structured, professional, and detailed writing.\n"
            "- Use tables, bullet points, and subheadings for clarity.\n"
            "- Include industry-specific examples and real-world cases.\n"
            "- Validate and enrich sections using external sources.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n\n"
            "Output:\n"
            "- Formal, structured, and client-ready document.\n"
            "- Include tables, and figures where necessary.\n"
            "- Maintain clarity, completeness, and professionalism.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n\n"
            "Every subpoint should be explained in an elaborated manner."
            ),
            expected_output=(
            "Clear and detailed sections for Introduction, Purpose, Scope, In Scope, Out of Scope, Assumptions, "
            "References, and Overview with enhanced explanations where needed. Every subpoint should be explained "
            "in an elaborated manner."
            ),
            agent=business_analyst
        )

        technical_analysis_task = Task(
            description=(
            "Objective:\n"
            "Extract and enhance sections from the Business Requirements Document (BRD):\n"
            "- Data Model\n"
            "- User Characteristics\n"
            "- Codification Schemes\n"
            "- Dependencies\n"
            "Enhance extracted sections with:\n"
            "- In-depth explanations\n"
            "- Real-world examples\n"
            "- Industry best practices\n"
            "- Structured details for client clarity\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n\n"
            "Guidelines:\n"
            "Data Model:\n"
            "- Extract existing model details and expand into a structured ER model.\n"
            "- Include entities, attributes, primary keys, foreign keys, and relationships.\n"
            "- Provide example schemas, sample data representations, and normalization best practices.\n"
            "- Use industry standards and tables where necessary.\n"
            "- No images or tables required\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "User Characteristics:\n"
            "- Identify and categorize user roles, personas, and access levels.\n"
            "- Include demographics, skill levels, and behavioral patterns.\n"
            "- Provide user journeys, workflows, and interaction models.\n"
            "- Incorporate UX/UI principles and accessibility considerations.\n"
            "- No images or tables required\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "Codification Schemes:\n"
            "- Extract existing schemes and document naming conventions.\n"
            "- Detail numbering systems, data classification rules, and coding structures.\n"
            "- Include examples of versioning strategies and hierarchical naming methods.\n"
            "- Align with industry standards (ISO, IEEE, enterprise policies).\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "Dependencies:\n"
            "- Identify internal and external dependencies affecting the system.\n"
            "- List third-party services, APIs, databases, regulatory constraints, and interdependencies.\n"
            "- Expand on bottlenecks, failure points, and contingency planning.\n"
            "- Provide risk assessments, mitigation strategies, and alternate solutions.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n\n"
            "Enhancements:\n"
            "- Validate vague sections using LLM and external industry sources.\n"
            "- Provide case studies, benchmarks, and best practices for enrichment.\n"
            "- Use tables, structured lists, flowcharts, and for clarity.\n"
            "- Maintain a structured, professional, and client-ready format.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n\n"
            "Output:\n"
            "- Highly detailed, structured, and professional document.\n"
            "- Include technical explanations, tables elements, and best practices.\n"
            "- Ensure exhaustive details for clarity and completeness.\n"
            "- Please elaborate the points properly where each point should be at least two paragraphs\n"
            "Every subpoint should be explained in an elaborated manner."
            ),
            expected_output=(
            "Clear and detailed technical sections for Data Model, User Characteristics, Codification Schemes, "
            "Assumptions, Dependencies, and Out of Scope. Every subpoint should be explained in an elaborated manner."
            ),
            agent=technical_analyst
        )

        requirement_categorize_task = Task(
            description=(
            "Objective:\n"
            "Extract and categorize business requirements from the Business Requirements Document (BRD) into:\n"
            "- Functional Requirements (FR)\n"
            "- Non-Functional Requirements (NFR)\n"
            "- Technical Requirements (TR)\n"
            "Enhance extracted requirements by:\n"
            "- Refining vague or unclear sections using LLM and external knowledge sources.\n"
            "- Providing detailed, structured, and client-ready documentation.\n\n"
            "Categorization Guidelines:\n"
            "Functional Requirements (FR):\n"
            "- Define core system features, operations, and expected behaviors.\n"
            "- Outline system responses to user actions.\n"
            "- Provide detailed use cases, workflows, and real-world examples.\n"
            "- Ensure all functionalities are measurable and verifiable.\n"
            "Non-Functional Requirements (NFR):\n"
            "- Define quality attributes, performance, security, scalability, and compliance needs.\n"
            "- Ensure all NFRs are quantifiable and testable (e.g., 'system must handle 1,000 transactions per second with 99.99% uptime').\n"
            "- Align with industry benchmarks and best practices.\n"
            "Technical Requirements (TR):\n"
            "- Extract infrastructure, technology stack, APIs, frameworks, and database structures.\n"
            "- Detail hardware/software constraints, networking requirements, and security protocols.\n"
            "- List third-party dependencies and integration requirements.\n"
            "- Enhance with best practices and current industry standards.\n\n"
            "Enhancements:\n"
            "- Identify and refine vague or ambiguous requirements.\n"
            "- Align with industry compliance and security standards.\n"
            "- Use tables, and structured lists for better clarity.\n"
            "- Ensure a structured, professional, and client-focused format.\n\n"
            "Output:\n"
            "- Well-structured, detailed, and categorized document.\n"
            "- Clear separation of Functional, Non-Functional, and Technical requirements.\n"
            "- Use of tables, bullet points, and tables elements for improved comprehension.\n"
            "- Comprehensive details ensuring no ambiguity in requirements."
            ),
            expected_output=(
            "A structured list of Functional, Non-Functional, and Technical requirements with well-explained descriptions."
            ),
            agent=requirement_categorizer
        )

        srs_write_task = Task(
            description=(
            "Objective:\n"
            "Generate a highly detailed, structured, and professional Software Requirements Specification (SRS) document by consolidating and expanding researched content.\n"
            "Ensure clarity, completeness, and technical accuracy while preserving extracted content where required.\n\n"
            "Guidelines:\n"
            "Preserve Extracted Content:\n"
            "- 'Out of Scope' and 'Assumptions' sections must be included exactly as extracted from the BRD without modification.\n"
            "- Expand all other sections with additional details but without altering the original intent.\n"
            "Sections to Include:\n"
            "- Introduction:\n"
            "  - Provide a project background, business context, and overall purpose.\n"
            "  - Include industry-specific context and real-world significance.\n"
            "- Purpose:\n"
            "  - Define the role of this document in guiding stakeholders.\n"
            "  - Clearly differentiate between business and technical objectives.\n"
            "- Scope:\n"
            "  - Outline explicit project boundaries, covering functional, non-functional, regulatory, and operational aspects.\n"
            "- In Scope:\n"
            "  - Break down included functionalities, features, and deliverables.\n"
            "  - Provide detailed descriptions, examples, and their business impact.\n"
            "- Out of Scope:\n"
            "  - Insert as-is from the BRD without modification.\n"
            "  - Provide additional context on exclusions and associated risks.\n"
            "- Assumptions:\n"
            "  - Insert as-is from the BRD without modification.\n"
            "  - Elaborate on implications and possible risks if assumptions change.\n"
            "- References:\n"
            "  - List cited materials, standards, frameworks, and relevant documentation.\n"
            "  - Add supporting industry best practices where applicable.\n"
            "- Overview:\n"
            "  - Summarize key takeaways in a structured, digestible format.\n"
            "Requirement Categorization:\n"
            "- Functional Requirements (FR):\n"
            "  - Define core system features, workflows, and expected behaviors.\n"
            "  - Provide detailed use cases, user interactions, and real-world applications.\n"
            "- Non-Functional Requirements (NFR):\n"
            "  - Outline performance expectations, security requirements, compliance standards, scalability, and operational constraints.\n"
            "  - Ensure quantifiable and testable criteria.\n"
            "- Technical Requirements (TR):\n"
            "  - Detail system architecture, technology stack, APIs, databases, integrations, hardware/software constraints, and security protocols.\n"
            "Technical Analysis & Data Representation:\n"
            "- Data Model:\n"
            "  - Expand with entity-relationship, database schemas, attribute definitions, and data flow explanations.\n"
            "  - Include normalization and optimization principles.\n"
            "- User Characteristics:\n"
            "  - Define user personas, roles, access levels, demographics, behavior patterns, and usability needs.\n"
            "  - Incorporate UX/UI principles for better accessibility.\n"
            "- Codification Schemes:\n"
            "  - Provide structured naming conventions, numbering systems, data classification rules, and version control strategies.\n"
            "  - Align with industry standards.\n"
            "Enhancements Using External Research & Best Practices:\n"
            "- Refine vague sections using LLM capabilities and external industry research to ensure clarity and completeness.\n"
            "- Incorporate real-world case studies, frameworks, standards, and benchmarks.\n"
            "- Utilize tables, flowcharts, and structured lists to enhance readability.\n"
            "- Maintain a formal, professional, and highly structured format suitable for clients and stakeholders.\n"
            "Output Requirements:\n"
            "- The final SRS document must be highly detailed, structured, and exhaustive.\n"
            "- Information should be well-organized and fully explained without ambiguity.\n"
            "- No modification should be made to sections explicitly required to remain unchanged.\n"
            "- The document must be formatted professionally, using clear headings, tables, and bullet points for readability.\n"
            "Every subpoint should be explained in an elaborated manner."
            ),
            expected_output=(
            "A fully written, structured, and polished SRS document incorporating all extracted and categorized information, ensuring that Out of Scope and Assumptions match the BRD and along with it every part must be defined in an elaborated manner. Every subpoint should be explained in an elaborated manner."
            ),
            agent=srs_writer,
        )

        srs_format_task = Task(
            description=(
            "Format the final SRS document with appropriate headings, line breaks, and structured sections.\n"
            "Ensure that the 'Out of Scope' section is correctly placed after 'In Scope'.\n"
            "Ensure that 'Assumptions' is correctly formatted with bullet points and listed before 'Dependencies'."
            ),
            expected_output=(
            "The final SRS document is properly formatted with bolded, capitalized headings, clear section divisions, and includes 'Out of Scope,' 'Assumptions,' 'Dependencies,' and 'Conclusion' sections saved as 'srs1.md'."
            ),
            agent=srs_formatter,
        )

        # Crew
        crew = Crew(
            agents=[business_analyst, technical_analyst, requirement_categorizer, srs_writer, srs_formatter],
            tasks=[business_analysis_task, technical_analysis_task, requirement_categorize_task, srs_write_task, srs_format_task],
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
st.markdown("Built by AgentcAI")


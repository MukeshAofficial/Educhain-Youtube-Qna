import streamlit as st
from educhain import Educhain, LLMConfig
from educhain.engines import qna_engine
from langchain_google_genai import ChatGoogleGenerativeAI

# Set page configuration at the very top of the script
st.set_page_config(page_title="Educhain YouTube Q&A", page_icon="🎥", layout="wide")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Google API Key", type="password")
    model_options = {
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-2.0-flash-lite-preview-02-05": "gemini-2.0-flash-lite-preview-02-05",
        "gemini-2.0-pro-exp-02-05": "gemini-2.0-pro-exp-02-05",
    }
    model_name = st.selectbox("Select Model", options=list(model_options.keys()), format_func=lambda x: model_options[x])

    st.markdown("**Powered by** [Educhain](https://github.com/satvik314/educhain)")
    st.write("❤️ Built by [Build Fast with AI](https://buildfastwithai.com/genai-course)")

# --- Initialize Educhain with Gemini Model ---
@st.cache_resource
def initialize_educhain(api_key, model_name):
    if not api_key:
        return None  # Return None if API key is missing

    gemini_model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key
    )
    llm_config = LLMConfig(custom_model=gemini_model)
    return Educhain(llm_config)


# --- Utility Function to Display Questions ---
def display_questions(questions):
    if questions and hasattr(questions, "questions"):
        for i, question in enumerate(questions.questions):
            st.subheader(f"Question {i + 1}:")
            if hasattr(question, 'options'):
                st.write(f"**Question:** {question.question}")
                st.write("Options:")
                for j, option in enumerate(question.options):
                    st.write(f"   {chr(65 + j)}. {option}")
                if hasattr(question, 'answer'):
                    st.write(f"**Correct Answer:** {question.answer}")
                if hasattr(question, 'explanation') and question.explanation:
                    st.write(f"**Explanation:** {question.explanation}")
            elif hasattr(question, 'keywords'):
                st.write(f"**Question:** {question.question}")
                st.write(f"**Answer:** {question.answer}")
                if question.keywords:
                    st.write(f"**Keywords:** {', '.join(question.keywords)}")
            elif hasattr(question,'answer'):
                st.write(f"**Question:** {question.question}")
                st.write(f"**Answer:** {question.answer}")
                if hasattr(question, 'explanation') and question.explanation:
                    st.write(f"**Explanation:** {question.explanation}")
            else:
                st.write(f"**Question:** {question.question}")
                if hasattr(question, 'explanation') and question.explanation:
                    st.write(f"**Explanation:** {question.explanation}")
            st.markdown("---")

# --- Streamlit App Layout ---
st.title("🎥 Educhain YouTube Q&A")

# --- Main Content: YouTube Q&A ---
if not api_key:
    st.warning("Please enter your Google API Key in the sidebar to continue.")
else:
    # Initialize Educhain client with Gemini model
    educhain_client = initialize_educhain(api_key, model_name)
    if educhain_client:
        qna_engine = educhain_client.qna_engine
        st.header("Generate Questions from YouTube")
        youtube_url = st.text_input("Enter YouTube Video URL:")
        num_questions_yt = st.slider("Number of Questions", 1, 5, 3, key="yt_q")
        question_type_yt = st.selectbox("Select Question Type", ["Multiple Choice", "Short Answer", "True/False", "Fill in the Blank"], key="yt_type")
        custom_instructions_yt = st.text_area("Custom Instructions (optional):", key="yt_ins", placeholder="e.g. 'Focus on key concepts'")

        if youtube_url and st.button("Generate Questions from YouTube", key='yt_button'):
            with st.spinner("Generating..."):
                questions = qna_engine.generate_questions_from_youtube(
                    url=youtube_url,
                    num=num_questions_yt,
                    question_type=question_type_yt,
                    custom_instructions=custom_instructions_yt
                )
                display_questions(questions)
    else:
        st.error("Failed to initialize Educhain. Please check your API key and model selection.")

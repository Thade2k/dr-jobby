import streamlit as st
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llm_module import ResumeAnalyzer
import uvicorn
import threading
import json
import os

# Initialize FastAPI app
app = FastAPI()

origins = ["*"]  # Allow all origins (for testing; restrict in production)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ResumeAnalyzer (outside of Streamlit's main function)
try:
    analyzer = ResumeAnalyzer()
except Exception as e:
    print(f"Error initializing analyzer: {e}")
    analyzer = None

# API Endpoint for Resume Analysis
@app.post("/analyze")
async def analyze_resume_api(file_path: str): # Expects a file path
    if analyzer is None:
        raise HTTPException(status_code=500, detail="Analyzer could not be initialized")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File path not found")
    try:
        analysis = analyzer.analyze_resume(file_path)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_resume_api(prompt: str, context: dict = None):
    if analyzer is None:
        raise HTTPException(status_code=500, detail="Analyzer could not be initialized")
    try:
        response = analyzer.chat_analyze(prompt, context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Streamlit App
def save_uploaded_file(uploaded_file):
    try:
        with open(uploaded_file.name, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return uploaded_file.name
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Resume Analyzer", layout="wide")
    st.title("Resume Analysis Assistant")
    st.write("Upload your resume and get professional feedback!")

    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    uploaded_file = st.file_uploader("Choose your resume", type=['pdf', 'docx'])

    if uploaded_file:
        with st.spinner("Analyzing resume..."):
            temp_file_path = save_uploaded_file(uploaded_file)
            if temp_file_path:
                try:
                    analysis = analyzer.analyze_resume(temp_file_path)
                    st.session_state.analysis_results = analysis
                    os.remove(temp_file_path)
                except Exception as e:
                    st.error(f"Analysis Error: {e}")
            else:
                st.error("Error saving uploaded file.")
    if st.session_state.analysis_results:
        # ... (rest of your Streamlit display code)
        st.subheader("Ask Questions")
        user_question = st.text_input("Ask about your resume:", key="user_input")
        if user_question:
            response = analyzer.chat_analyze(user_question, st.session_state.analysis_results)
            st.write("Response:", response)

# Run both Streamlit and FastAPI
if __name__ == "__main__":
    import threading

    def run_streamlit():
        main()
    def run_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=8000)

    streamlit_thread = threading.Thread(target=run_streamlit)
    fastapi_thread = threading.Thread(target=run_fastapi)

    streamlit_thread.start()
    fastapi_thread.start()
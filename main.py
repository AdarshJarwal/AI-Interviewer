import os
import re
import time
import uuid
import base64
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
from groq import Groq

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.agents import create_agent

# --- 1. ENVIRONMENT & BACKEND SETUP ---
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
# Gemini Model
model1 = init_chat_model("google_genai:gemini-2.5-flash-lite")

# Grok Model
model2 = init_chat_model("groq:qwen/qwen3-32b")

# Anthropic Model
model3 = init_chat_model("anthropic:claude-sonnet-4")


# Helper function to clean AI output
def clean_output(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# Initialize Database Checkpointer
conn = sqlite3.connect("AI_interviewer_history.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)



def run_timer(seconds, message, container):

    """Displays a visual countdown timer in a Streamlit container."""

    for i in range(seconds, 0, -1):
        container.warning(f"⏳ **{message}**: {i} seconds remaining...")
        time.sleep(1)
        container.empty()


def get_interview_agent(topic, difficulty, ques, resume= None):
    sys_prompt = f"""
    You are a strict but fair professional technical interviewer specializing in {topic}.
    CRITICAL RULES FOR EVERY RESPONSE:
    1. NEVER answer your own questions. Wait for the user to answer.
    2. Ask total {ques} one by one ,each after user answers.
    if no questions are left, give only feedback.
    3. Format your response EXACTLY like this:
       **Feedback:** [1-2 sentences briefly evaluating their answer, dont say the word feedback]\n\n
       **Next Question:** [Ask exactly ONE new {difficulty}-difficulty technical question]
    4. You can also ask questions from the resume ({resume})
    4. Do NOT break character. Just provide the feedback, score, and immediately ask the next question.
    5. Ask questions an average student can answer in 90 sec of speech.
    6. Evaluate on conceptual clarity, not memorization.
    """
    return create_agent(
        model1,
        tools=[],
        checkpointer=checkpointer,
        system_prompt=sys_prompt
    )


# --- 2. AUDIO UTILITIES ---

def output_audio_from_text(text_to_speak):
    """Converts text to speech and autoplays it."""
    audio_filename = "temp_output.mp3"
    tts = gTTS(text=text_to_speak, lang='en', slow=False)
    tts.save(audio_filename)

    with open(audio_filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()

    html_audio = f"""
        <audio autoplay="true" style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(html_audio, unsafe_allow_html=True)



def transcribe_audio_groq(audio_bytes):
    """Transcribes audio using Groq's Whisper model."""
    try:
        with open("temp_mic.wav", "wb") as f:
            f.write(audio_bytes.read())

        with open("temp_mic.wav", "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=("temp_mic.wav", file.read()),
                model="whisper-large-v3",
                response_format="text",
                language="en"
            )
        return transcription
    except Exception as e:
        return f"[Error transcribing audio: {str(e)}]"


# --- 3. STREAMLIT UI & SESSION STATE ---
st.set_page_config(page_title="AI Interviewer", page_icon="🎙️", layout="wide")

# Initialize session states
if "interview_state" not in st.session_state:
    st.session_state.interview_state = "setup"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}
if "current_ai_text" not in st.session_state:
    st.session_state.current_ai_text = ""
if "audio_played" not in st.session_state:
    st.session_state.audio_played = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Interview Settings")
    topic_input = st.text_input("Topic", value="Data Structures and Algorithms")
    diff_input = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
    num_que_input = st.number_input("Number of Questions", min_value=3, max_value=20, value=5)
    resume_file = st.file_uploader("Upload your resume (pdf only)", type=["pdf"])
    if st.button("Reset Session", type="secondary"):
        st.session_state.clear()
        st.rerun()

st.title("🎙️ AI Technical Interviewer")

# PHASE 1: SETUP
if st.session_state.interview_state == "setup":
    st.info(f"Mock Interview: **{diff_input}** level on **{topic_input}** ({num_que_input} questions).")

    st.markdown("""
    ### Instructions:
    1. The AI will ask you to introduce yourself.
    2. Ensure your environment is quiet.
    3. Use the microphone widget to record your answers.
    4. You will get 90 seconds to record your ans.
    5. You can also attach your resume in the sidebar to get more personalized interview.
    """)


    if st.button("Start Interview", type="primary"):
        st.session_state.topic = topic_input
        st.session_state.difficulty = diff_input.lower()
        st.session_state.num_que = num_que_input
        st.session_state.interview_state = "intro"
        st.rerun()

# PHASE 2: INTRO
elif st.session_state.interview_state == "intro":
    st.write("### Please give a brief introduction about yourself.")
    intro_msg = "Please give a brief introduction about yourself."

    # Play Audio once
    if not st.session_state.audio_played:
        output_audio_from_text(intro_msg)
        st.session_state.audio_played = True

    # Record User Answer safely
    user_intro_audio = st.audio_input("Record your Intro", key="intro_audio")
    time_placeholder = st.empty()

    if user_intro_audio is None:
        run_timer(60, "Speak in the time window", time_placeholder)

    if user_intro_audio is not None :
        with st.spinner("Processing audio..."):
            user_intro = transcribe_audio_groq(user_intro_audio)

        st.success(f"**You said:** {user_intro}")
        st.session_state.messages.append({"role": "user", "content": user_intro})

        # Generate first question
        with st.spinner("Generating your first question..."):
            agent = get_interview_agent(st.session_state.topic, st.session_state.difficulty, st.session_state.num_que,
                                        resume= resume_file)
            res = agent.invoke(
                {'messages': [HumanMessage(content=f"{user_intro}. I am ready for the first question.")]},
                config=st.session_state.config
            )
            ai_reply = clean_output(res['messages'][-1].content)

            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.session_state.current_ai_text = ai_reply
            st.session_state.interview_state = "interviewing"
            st.session_state.audio_played = False  # Reset for next phase
            st.rerun()

# PHASE 3: INTERVIEWING LOOP
elif st.session_state.interview_state == "interviewing":

    # Render previous conversation
    for msg in st.session_state.messages[:-1]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Render current AI message
    with st.chat_message("assistant"):
        st.markdown(st.session_state.current_ai_text)

    # Check if we should continue asking questions
    if st.session_state.question_count < st.session_state.num_que:
        st.markdown("---")

        # Play audio once per question
        if not st.session_state.audio_played:
            output_audio_from_text(st.session_state.current_ai_text)
            st.session_state.audio_played = True

        # Unique key forces the audio widget to reset for each question
        audio_key = f"ans_audio_{st.session_state.question_count}"
        user_ans_audio = st.audio_input("Record your answer", key=audio_key)
        time_placeholder = st.empty()

        if user_ans_audio is None:
            run_timer(90, "Speak in the time window", time_placeholder)

        if user_ans_audio is not None:
            with st.spinner("Transcribing..."):
                user_ans = transcribe_audio_groq(user_ans_audio)

            st.session_state.messages.append({"role": "user", "content": user_ans})
            st.success(f"**You answered:** {user_ans}")

            # Get AI Evaluation & Next Question
            with st.spinner("Evaluating and formulating next question..."):
                agent = get_interview_agent(st.session_state.topic, st.session_state.difficulty)
                response = agent.invoke(
                    {"messages": [HumanMessage(content=user_ans)]},
                    config=st.session_state.config
                )
                ai_reply = clean_output(response['messages'][-1].content)

            # Update state
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.session_state.current_ai_text = ai_reply
            st.session_state.question_count += 1
            st.session_state.audio_played = False  # Reset for the new AI message
            st.rerun()

    else:
        st.success("Interview completed! Generating final report...")
        if st.button("View Final Report", type="primary"):
            st.session_state.interview_state = "report"
            st.rerun()

# PHASE 4: REPORT
elif st.session_state.interview_state == "report":
    with st.spinner("Compiling your feedback report..."):
        report_prompt = """
        The interview is now over. Generate a final interview report based on the history.
        Format EXACTLY with these headings:
        - Overall Score (Average out of 10)
        - Strengths
        - Weaknesses
        - Improvement Tips
        """
        agent = get_interview_agent(st.session_state.topic, st.session_state.difficulty)
        report_res = agent.invoke(
            {"messages": [HumanMessage(content=report_prompt)]},
            config=st.session_state.config
        )
        final_report = clean_output(report_res['messages'][-1].content)

        st.markdown("## 📊 Final Interview Report")
        st.markdown(final_report)

    if st.button("Return to Home"):
        st.session_state.clear()
        st.rerun()
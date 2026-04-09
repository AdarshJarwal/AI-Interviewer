
# 🎙️ AI Technical Interviewer

A fully interactive, voice-enabled AI Mock Interview application built with Streamlit and LangChain. This tool simulates a realistic technical interview environment by listening to your spoken answers, evaluating them in real-time using large language models, and asking dynamic follow-up questions based on your performance and resume.

## ✨ Features

* **Voice-to-Text & Text-to-Voice:** Speak your answers naturally using your microphone, and hear the AI interviewer speak back to you using `gTTS` and Groq's Whisper model.
* **Intelligent AI Agent:** Powered by LangChain and Google's Gemini (with options for Groq/Anthropic), the AI acts as a strict but fair technical interviewer.
* **Customizable Sessions:** Choose your interview topic, difficulty level (Easy, Medium, Hard), and the number of questions.
* **Resume Integration:** Upload your PDF resume so the AI can ask personalized questions based on your background.
* **Comprehensive Final Report:** At the end of the session, receive a detailed grading report including an overall score, strengths, weaknesses, and actionable improvement tips.
* **State Management:** Uses LangGraph and SQLite to maintain conversational memory and interview state across the session.

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI Orchestration:** [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)
* **Audio Processing:** `st.audio_input`, Groq Whisper API (Transcription), `gTTS` (Speech Synthesis)
* **LLM Providers:** Google Gemini, Groq, Anthropic
* **Database:** SQLite (for chat history checkpointing)

## ⚙️ Prerequisites

Before you begin, ensure you have Python 3.9+ installed. You will also need API keys for the AI services used in this project:
* [Google Gemini API Key](https://aistudio.google.com/)
* [Groq API Key](https://console.groq.com/)
* [Anthropic API Key](https://console.anthropic.com/) *(Optional, based on your active model)*

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/AdarshJarwal/AI-Interviewer-app.git](https://github.com/AdarshJarwal/AI-Interviewer-app.git)
cd AI-Interviewer-app
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up Environment Variables**
Create a `.env` file in the root directory and add your API keys:
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## 🎮 How to Run

Start the Streamlit server by running the following command in your terminal:

```bash
streamlit run app.py
```

The application will open automatically in your default web browser at `http://localhost:8501`.

## 📖 Usage Instructions

1. **Configure Interview:** Open the sidebar to enter your desired topic (e.g., "React Native", "System Design"), select the difficulty, and set the number of questions.
2. **Upload Resume:** (Optional) Attach your resume in PDF format in the sidebar.
3. **Start:** Click **Start Interview**.
4. **Introduction:** Listen to the AI's prompt, click the microphone widget, record your introduction, and click Stop to submit.
5. **The Interview:** The AI will evaluate your answer, provide feedback, and ask the next question. Record your answer within the suggested 90-second window.
6. **Feedback Report:** Once all questions are answered, click "View Final Report" to see your overall score and feedback.

## 📂 Project Structure

```text
ai-interviewer-app/
│
├── .env                     # API Keys (Do not commit to version control)
├── .gitignore               # Ignored files (temp audio, databases, etc.)
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── app.py                   # Main Streamlit application
│
└── AI_interviewer_history.db # Auto-generated SQLite database for memory
```

## ⚠️ Notes
* **Audio Files:** The app creates temporary audio files (`temp_mic.wav` and `temp_output.mp3`) during runtime. These are overwritten with each new question.
* **Environment:** Ensure you are in a quiet environment for the best transcription accuracy from the Whisper model.
```

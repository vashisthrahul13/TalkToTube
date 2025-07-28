## TalktoTube 

A **Chrome extension** that lets you ask questions about any YouTube video and get answers directly — powered by **FastAPI**, **LangChain**, **FAISS**, and **OpenAI GPT** via **RAG** (Retrieval-Augmented Generation).
It also shows **relevant timestamps** where your query is discussed and allows **in-tab seeking** in the video.

---

### Features

* Ask natural language questions about any YouTube video.
* Uses the video's transcript + GPT model to generate accurate answers.
* Displays relevant **timestamped snippets** with clickable links.
* Click a timestamp to **seek the video in the same tab** — no reload!
* FastAPI backend with LangChain, FAISS, and OpenAI integration.
* Local-only (no data is stored), secure, and fast.

---

### Demo

![Demo](https://github.com/vashisthrahul13/TalkToTube/blob/master/Resources/TalktoTube-Demo.gif)

---

## Getting Started

### 🔁 Clone the repo

```bash
git clone https://github.com/yourusername/youtube-chatbot-rag.git
cd youtube-chatbot-rag
```

---

## 🔩 Chrome Extension Setup

1. Go to `chrome://extensions/` in Chrome.
2. Enable **Developer Mode**.
3. Click **Load unpacked** and select the `chrome-extension/` directory.
4. Pin the extension and click it on any YouTube video.
5. Ask a question — the answer and timestamps will appear!

---

## ⚙️ Backend Setup (FastAPI)

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the root or backend directory:

```env
OPENAI_API_KEY=your_openai_api_key
```

### 4. Start the FastAPI server

```bash
uvicorn api:app --reload
```

Now your API is available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

You can test it at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Features in Detail

### Retrieval-Augmented Generation

* Extracts YouTube transcript using `youtube_transcript_api`
* Chunks the transcript using `RecursiveCharacterTextSplitter`
* Embeds chunks with `OpenAIEmbeddings`
* Stores vectors in-memory with `FAISS`
* Retrieves relevant chunks via `MMR` search
* Passes results to OpenAI GPT model using a structured prompt

### Timestamped Responses

* Each retrieved chunk includes its original transcript `start` time.
* The extension converts it to `mm:ss` and allows **in-tab seeking**.
* No reloading or new tabs — it interacts directly with the video element.

---

## 🛠 Future Improvements

* [ ] Add support for multilingual transcripts
* [ ] Store past queries locally
* [ ] Allow user to select between answers based only on video context or general GPT intelligence
* [ ] Show related follow-up questions

---
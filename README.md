# Promptify

Promptify is a Chrome extension that helps you structure and scope your prompts before sending them to AI coding agents. By analyzing your raw idea, it suggests the appropriate tier of complexity and generates a structured prompt, PRD, or Technical Design Document based on that tier.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/immessy/Promptify.git
   cd Promptify
   ```

2. **Install server dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r server/requirements.txt
   ```

3. **Configure Environment Variables:**
   You can run this project using a free Google Gemini API key or entirely locally using Ollama.
   Copy the example environment file:
   ```bash
   cp server/.env.example server/.env
   ```
   * **To use Google Gemini (Recommended, Free):** Get an API key from [Google AI Studio](https://aistudio.google.com/) and add it to `GEMINI_API_KEY` in your `.env` file.
   * **To use Ollama (Local, Offline):** Install and run [Ollama](https://ollama.com/), pull the `llama1.1` model, and leave the `GEMINI_API_KEY` blank. It will automatically fall back to your local Ollama instance on `localhost:11434`.

## Running the Server

Start the local "brain" backend:
```bash
cd server
python app.py
```
The server will run on `http://localhost:5000`.

## Loading the Extension

1. Open Google Chrome and navigate to `chrome://extensions`.
2. Enable **Developer Mode** in the top right corner.
3. Click **Load unpacked** in the top left.
4. Select the `extension/` folder from this repository.

## Usage

1. Open the Promptify Side Panel in Chrome (by clicking the extension icon or the side panel button).
2. Type your rough, unstructured task idea into the text area and click **Suggest tier**.
3. The AI will analyze your idea, suggest a tier (Novice, Intermediate, or Production), and provide its reasoning.
4. You can confirm the suggested tier or manually override it using the dropdown.
5. Click **Generate** to create the structured documents (Prompt, PRD, TDD, etc.).
6. Click **Copy** on any generated document to paste it into your AI coding agent (Claude, Gemini, Antigravity, etc.).

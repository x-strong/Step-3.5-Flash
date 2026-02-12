# Hybrid Local Agent on MacOS

Build a private, local Agentic Sandbox on MacOS (Apple Silicon) using a **Hybrid Architecture** that optimizes cost and latency:

1.  **Brain (Step 3.5 Flash):** Complex reasoning, planning, and tool selection via `llama.cpp`.
2.  **Janitor (Qwen 2.5 Coder):** Routine tasks (syntax fixing, summarization) via Ollama, saving efficient tokens.
3.  **Hands (MCP Server):** Safe access to local tools (Apple Mail, Playwright, Python Sandbox).

## 🌟 Features

*   **Native MacOS Integration:** Automate Apple Mail via AppleScript.
*   **Secure Python Sandbox:** AST-validated execution for generated code.
*   **RAG Memory:** Local ChromaDB for long-term retention.
*   **Bandwidth Optimization:** Compresses web content locally before reasoning.

## 🛠 Prerequisites

* **Hardware:** Mac with Apple Silicon (M1/M2/M3). Tested on M3 Max (128GB).
* **Software:**
    * Python 3.10+
    * [Ollama](https://ollama.com/) (for the Janitor model)
    * `llama-server` (built from source or installed via brew) running Step 3.5 Flash.

## 📦 Installation

1.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

2.  **Prepare the Models:**
    * **Janitor:** Run `ollama run qwen2.5-coder:3b` in a terminal.
    * **Brain:** Ensure your Step 3.5 Flash `llama-server` is running on port 8080 (or update the URL in the configuration).

    *M3 Max Optimization (adjust wired limit for large contexts):*
    ```bash
    sudo sysctl iogpu.wired_limit_mb=125000
    ```

## 🚀 Usage

1.  **Start the MCP Server:**
    ```bash
    python main.py
    ```

2.  **Connect your Client:**
    Use an MCP-compatible client (like Claude Desktop or a custom script) and point it to this server command.

3.  **Example Prompts:**
    * *"Check my unread emails from the 'IA_INBOX' folder and summarize the newsletter."*
    * *"Go to [url], fetch the content, summarize it using the Janitor, and save the key points to memory."*

## ⚠️ Notes

* **Privacy:** All data (emails, memory, RAG) stays strictly local in the `./data` folder.
* **Safety:** The Python execution tool blocks dangerous imports (`os`, `sys`, `socket`) by default.
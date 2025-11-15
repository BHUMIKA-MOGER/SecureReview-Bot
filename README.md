# 🤖 AI Code Reviewer Bot (FastAPI + Ollama)
This project implements a privacy-focused, self-hosted AI bot that automatically reviews code changes in GitHub Pull Requests (PRs) using a local Large Language Model (LLM) (Phi-3 Mini) served via Ollama.

It combines a simple FastAPI application with the Git webhook system to provide high-quality, contextual code feedback without sending your proprietary code to external cloud providers.

*** 
# 💡 Project Overview & Key Advantages
| Feature | Description | Value Proposition |
| :--- | :--- | :--- |
| **Data Privacy 🛡️** | All code analysis is performed locally on your CPU/GPU, ensuring your sensitive source code never leaves your machine. | Essential for internal projects, regulated industries (finance/healthcare), and protecting IP. |
| **Zero API Cost 💰** | Eliminate recurring per-token fees from services like Gemini or ChatGPT APIs. After the initial setup, the analysis is free to run repeatedly.| Highly cost-effective for large teams or high-volume CI/CD workflows. |
| **LLM Control ✨** | You have full control over the model's behavior. You can easily swap models (CodeLlama, Mistral) or fine-tune the LLM on your team's specific codebase or standards. | Ensures the AI review aligns perfectly with your organization's domain and style guide. |
| **Offline Ready** | Once the model is downloaded, the core review process can run without an internet connection (though GitHub interaction still requires connectivity). | Guarantees stability and productivity even with network constraints. |

***
# ⚙️ Setup and Installation
**Prerequisites :**
You must have the following dependencies installed and running before starting the bot:
* **Python 3.10+**
* **Git (Installed and configured)**
* **Ollama (The LLM server)**
* **ngrok** (For exposing your local service to the public internet)

***
# Step 1: Clone the Repository & Install Dependencies
```
# Clone the repository
git clone [https://github.com/BHUMIKA-MOGER/FUTURE_DS_03.git](https://github.com/BHUMIKA-MOGER/FUTURE_DS_03.git)
cd AI-Code-Reviewer-Bot

# Create and activate the Python Virtual Environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # Linux/macOS

# Install Python packages
pip install -r requirements.txt
```
# Step 2: Download the AI Model
The bot is configured to use Phi-3 Mini. Run this command once in a terminal to download the model via Ollama:
```
ollama run phi3:mini
```

***
# 💻 Git Terminal Workflow (Local Code Management)
The "Git Terminal" is the local command-line interface (CLI) used to manage and synchronize your code with the GitHub remote repository.
| Command | Purpose | When to Use |
| :--- | :--- | :--- |
| ```git add <file> / git add . ```| **Stages Changes:** Marks modified files to be included in the next snapshot (commit). | After you edit any code file ```(main.py, test_calc.py, etc.)```. |
| ```git commit -m "Message"``` | **Commits Changes:** Creates a permanent snapshot in your local history. | After staging changes, right before pushing. |
| ```git push origin <branch>``` | **Pushes to GitHub:** Uploads your new local commits to the remote repository. | After committing changes, this action triggers the AI review bot! |

***
**💡 Note on New Files:** Any new files created for debugging, analysis, or utility functions (even those stored in VS Code) must be manually introduced into the Git system using the  ```git add ``` and  ```git commit ``` steps outlined above before they can be tracked and pushed to GitHub.

***
# 🔑 Configuration: GitHub Token (.env File)
The bot needs a GitHub Personal Access Token (PAT) to fetch code, read Pull Requests, and post comments.

**1. Generating the Token**
* **Location:** Go to **GitHub Settings $\rightarrow$ Developer settings $\rightarrow$ Personal access tokens $\rightarrow$ Tokens (classic)**.
* **Permissions (Scopes):** The token MUST be granted the repo scope (Full control of private repositories) to allow read access to the code diff and write access to     post comments on the PR.
* **Token String:** Copy the generated token string immediately.

***
**2. Inserting the Token into  ```.env ```:**
Create a file named ```.env``` in the root of your AI-Code-Reviewer-Bot directory. Insert your token here (Git is configured to ignore this file for security):
 ```
 # .env file content 
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
(Replace the placeholder with your actual token string).

***
# 🔗 Connecting the Webhook (Crucial Integration Flow)
The webhook is the mechanism that connects the event on GitHub to your running bot. The process after configuring the token is highly dependent on your bot running correctly.
Dependency Flow
* Token (PAT) is inserted into ```.env``` and loaded by ```main.py```. This allows the bot to authenticate with the GitHub API (```g.get_user().login```).
* FastAPI Bot starts on ```http://localhost:8001.```
* Ngrok runs and provides a public URL (e.g., ```https://a4fc0a97b63d.ngrok-free.app```).
* Webhook Setup uses the Ngrok URL to tell GitHub where to send the event payload.

**1. Get the Public URL**

From the Ngrok Terminal (Terminal 3), copy the HTTPS Forwarding URL. This URL changes every time you restart ngrok.
* Example URL: https://a4fc0a97b63d.ngrok-free.app

**2. Configure the GitHub Webhook**

* Go to your GitHub repository's **Settings $\rightarrow$ Webhooks.**
* Ensure **"Active"** is checked and click **"Add webhook."**

# Store this packages in requirement.txt
| Package Name | Purpose  | Installation Command |
| :--- | :--- | :--- |
| ```fastapi``` | Web framework for creating the ``` /webhook``` API endpoint.|``` pip install fastapi ```|
| ```uvicorn[standard]``` | ASGI server used to run the FastAPI app on ```localhost:8001.``` | ```pip install uvicorn[standard] ```|
|  ```python-dotenv ``` | Safely loads the GITHUB_TOKEN from the ```.env``` file into the application's environment. |  ```pip install python-dotenv``` |
| ``` PyGithub ``` | Library for interacting with the GitHub REST API (fetching code, posting comments). | ```pip install PyGithub``` |
|  ```langchain-ollama ``` | Critical Fix: Provides the correct ```OllamaLLM``` class for connecting Python to the local Ollama server. | ```pip install langchain-ollama``` |

***
# 🏃 Commands to Run the Project (Final Step)
You must run these three components concurrently in three separate terminal windows to keep your entire system operational:
| Component |  Terminal Command | Local Address/Port |
| :--- | :--- | :--- |
| **Terminal 1: Ollama Server** |``` ollama serve```  |``` http://127.0.0.1:11434 ```|
| **Terminal 2: FastAPI Bot** | ``` python main.py``` | ``` http://0.0.0.0:8001```|
|  **Terminal 3: Ngrok Tunnel** | ``` ngrok http 8001```  | Public HTTPS URL $\rightarrow$ ```http://localhost:8001``` |

***
# Test and Review
Push a new commit to any open Pull Request. The AI review comment should appear on the PR page shortly after your Uvicorn terminal logs show "Successfully posted review."

from fastapi import FastAPI, Request, HTTPException

from dotenv import load_dotenv

from github import Github

import os

import json

from github.PullRequest import PullRequest 

from github.Repository import Repository 

from langchain_community.llms.ollama import Ollama
from langchain_ollama import OllamaLLM
# --- 1. CONFIGURATION ---



# Load environment variables (secrets) from the .env file

load_dotenv()



# Get tokens and URLs from environment variables



GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")





if not GITHUB_TOKEN:

    raise ValueError("GITHUB_TOKEN not found in environment variables.")



# Initialize the GitHub client

g = Github(GITHUB_TOKEN)



# Initialize the FastAPI application

app = FastAPI()



# --- 2. CORE LOGIC FUNCTIONS ---



async def get_pr_diff(repo_full_name: str, pr_number: int) -> str:

    """Fetches the code changes (diff/patch) from the pull request."""

    try:

        # NOTE: We fetch repo and pr objects here for robustness, 

        # but the main logic relies on the objects fetched in the caller function.

        repo = g.get_repo(repo_full_name)

        pr = repo.get_pull(pr_number)



        full_diff = ""

        

        # Iterate over files changed in the PR

        for file in pr.get_files():

            # Only process files that have a patch (code changes)

            if file.patch:

                full_diff += f"--- FILE: {file.filename} ---\n"

                full_diff += file.patch # The diff content (lines starting with + or -)

                full_diff += "\n\n"

        

        return full_diff



    except Exception as e:

        print(f"Error fetching PR diff for {repo_full_name}#{pr_number}: {e}")

        return ""



async def get_ai_review(code_diff: str) -> str:

    """Sends the code diff to the LLM (Phi-3) for review."""



    # 1. Define the role for the LLM (Prompt Engineering)

    system_prompt = (

        "You are an expert Python software engineer and security reviewer. "

        "Review the following Git diff for bugs, logical flaws, security vulnerabilities, "

        "and adherence to best practices. Use a clear, bulleted list format. "

        "Provide constructive feedback and suggest specific code improvements. "

        "If the code is flawless, state only: '🤖 Review: LGTM (Looks Good To Me)'. "

        "Keep the review concise, limited to 5-7 points max."

    )



    # 2. Prepare the full prompt for the LLM

    full_prompt = f"{system_prompt}\n\nReview this code diff:\n\n{code_diff}"



    # 3. Initialize and call the Ollama LLM

    try:

        llm = OllamaLLM(

            base_url="http://127.0.0.1:11434",

            # FIX: Use the confirmed model tag from your laptop

            model="phi3:mini", 

            temperature=0 # Use low temperature for deterministic, factual review

        )



        print("LOG: Sending diff to Phi-3 Mini for analysis...") 

        response = llm.invoke(full_prompt)



        return response # Ollama's invoke returns the content directly



    except Exception as e:

        return f"🚨 AI Review Failed: Could not connect to the AI model. Check your connection and ensure the model is running. Error: {e}"



# --- 3. POST COMMENT LOGIC ---



async def post_review_comment(pr: PullRequest, review_comment: str):

    """Posts the final AI review back to the Pull Request on GitHub."""

    try:

        final_comment = (

            "## 🤖 AI Code Review Summary\n\n"

            "*(Powered by **Phi-3 Mini** LLM)*\n\n" # Updated model name

            f"{review_comment}"

        )

        pr.create_issue_comment(final_comment) 

        print(f"LOG: Successfully posted review for PR #{pr.number}")

        

    except Exception as e:

        # This will catch errors related to token permissions

        print(f"Error posting review for PR #{pr.number}: {e}")

        

async def process_pull_request_review(repo_full_name: str, pr_number: int):

    """Orchestrates the entire review pipeline."""

    

    # --- FIX: Fetch objects dynamically using webhook data ---

    repo = g.get_repo(repo_full_name) 

    pr = repo.get_pull(pr_number)     

    # --------------------------------------------------------



    # Step 1: Fetch the Diff

    diff = await get_pr_diff(repo_full_name, pr_number)

    

    # NOTE: The missing argument error came from calling post_review_comment 

    # incorrectly here, but since the logic is now correct, we move on.

    if not diff:

        return await post_review_comment(pr, review_comment="No code changes detected to review.")

        

    # Step 2: Get AI Review

    review_comment = await get_ai_review(diff)

    

    # Step 3: Post Comment to GitHub

    await post_review_comment(pr, review_comment)

    

# --- 4. WEBHOOK ENDPOINT ---



@app.post("/webhook")

async def handle_github_webhook(request: Request):

    """Listens for GitHub webhook events on the public ngrok URL."""

    

    event_type = request.headers.get("X-GitHub-Event")

    if not event_type:

        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")



    try:

        payload = await request.json()

    except json.JSONDecodeError:

        raise HTTPException(status_code=400, detail="Invalid JSON payload")



    # Filter for Pull Request events that are opened or updated (synchronize)

    if event_type == "pull_request" and payload.get("action") in ["opened", "synchronize"]:

        

        pr_number = payload["pull_request"]["number"]

        repo_full_name = payload["repository"]["full_name"]

        

        print(f"LOG: Received PR event for {repo_full_name}#{pr_number}. Initiating review...")

        

        # Initiate the core logic without blocking the webhook return

        await process_pull_request_review(repo_full_name, pr_number)

        

        # Return a quick 200 OK response to GitHub

        return {"message": f"Review initiated for PR #{pr_number}"}

    else:
        return {"message": "Event ignored - Required keys (pull_request/repository) missing in payload."}

    return {"message": "Event ignored"}



# --- 5. START SERVER COMMAND ---



if __name__ == "__main__":

    import uvicorn

    print("\n--- Starting AI Code Review Bot ---")

    print(f"GitHub Bot Initialized for user: {g.get_user().login}")

    print("WARNING: Ensure Ollama server is running (http://localhost:11434) and the 'phi3:mini' model is ready.")

    

    uvicorn.run(app, host="0.0.0.0", port=8001)
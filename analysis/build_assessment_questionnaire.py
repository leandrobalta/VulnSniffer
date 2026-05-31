import os
import sys
import json
import time
import csv
import logging
import pandas as pd
import requests
from openai import OpenAI

# ---------------------------------------------------------------------------
# CONFIGURATION & SETTINGS
# ---------------------------------------------------------------------------
INPUT_CSV = "results_audit_sample.csv"
OUTPUT_JSON = "vulnerability_questionnaire.json"
OUTPUT_CSV = "vulnerability_questionnaire.csv"
CACHE_FILE = "repo_analysis_cache.json"

# Retrieve API Keys from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Recommended to avoid rate limits
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Mapping your detection types to standard Common Weakness Enumerations (CWE)
CWE_MAPPING = {
    "INSECURE_CORS": "CWE-942: Permissive Cross-Domain Policy with Wildcard",
    "NESTJS_MASS_ASSIGNMENT": "CWE-915: Improper Modification of Dynamically-Determined Object Attributes",
    "DB_AUTO_SYNC": "CWE-1188: Insecure Default Initialization of Resource (Schema Auto-Sync Enabled)",
    "HARDCODED_SECRET": "CWE-798: Use of Hardcoded Credentials"
}

# Setup logger for tracing execution and handling failures gracefully
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Initialize OpenAI client if API key is provided
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def load_cache():
    """Loads the repository analysis cache from disk to minimize LLM calls."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load cache file, starting fresh. Error: {e}")
    return {}

def save_cache(cache):
    """Saves the updated repository analysis cache to disk."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to write cache file: {e}")

def fetch_github_file_with_retry(repo, file_path, token=None):
    """
    Downloads the raw source file from GitHub. 
    Handles common branch variations (main vs master) and rate limit statuses.
    """
    headers = {"Authorization": f"token {token}"} if token else {}
    branches = ["main", "master"]
    
    for branch in branches:
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"
        try:
            response = requests.get(raw_url, headers=headers, timeout=15)
            
            # Handle rate limit warnings from GitHub header
            if "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining"])
                if remaining < 5:
                    logging.warning("GitHub API rate limit running low. Sleeping for 5 seconds...")
                    time.sleep(5)
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                logging.warning("Hit 429 Too Many Requests. Backing off for 30 seconds...")
                time.sleep(30)
        except requests.RequestException as e:
            logging.error(f"Network error trying to fetch {file_path} from branch {branch}: {e}")
            
    return None

def fetch_repo_context_for_llm(repo, token=None):
    """Fetches general repository information (description or README headers) to feed the LLM context."""
    headers = {"Authorization": f"token {token}"} if token else {}
    api_url = f"https://api.github.com/repos/{repo}"
    
    context_str = f"Repository Name: {repo}\n"
    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            context_str += f"GitHub Description: {data.get('description', 'None provided')}\n"
            context_str += f"Topics/Keywords: {', '.join(data.get('topics', []))}\n"
    except Exception as e:
        logging.warning(f"Could not fetch API metadata for {repo}: {e}")

    # Fallback to try fetching a snippet of the README for additional semantic context
    readme_content = fetch_github_file_with_retry(repo, "README.md", token)
    if readme_content:
        context_str += f"\nREADME Snippet:\n{readme_content[:1000]}"
        
    return context_str

def generate_ai_project_description(repo, context_data):
    """Uses OpenAI Chat Completion API to generate a high-quality summary of the repository."""
    if not openai_client:
        return "AI Description Unavailable (No OPENAI_API_KEY provided)."
    
    prompt = (
        f"Analyze the following metadata/README of a GitHub repository:\n\n{context_data}\n\n"
        "Generate a concise project summary in English (exactly 2 to 5 sentences) explaining:\n"
        "1. The project's primary purpose.\n"
        "2. Its main technologies/frameworks (specifically looking for TypeScript/Node.js backends).\n"
        "3. Its likely real-world use case or academic scope.\n"
        "Be professional, direct, and do not include meta-commentary like 'Based on the provided information'."
    )
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Highly cost-effective and perfectly optimized for summaries
            messages=[
                {"role": "system", "content": "You are a senior technical writer and security researcher assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"LLM generation failed for {repo}: {e}")
        return "Error generating project description via LLM."

def extract_code_snippet(file_content, target_line, context_lines=10):
    """
    Extracts a file slice surrounding the vulnerable target line, adding contextual markers 
    and line numbers so experts don't lose perspective.
    """
    if not file_content:
        return "Source code could not be downloaded."
        
    lines = file_content.splitlines()
    total_lines = len(lines)
    
    # Core mathematical array boundary clipping
    center_idx = int(target_line) - 1
    start_idx = max(0, center_idx - context_lines)
    end_idx = min(total_lines - 1, center_idx + context_lines)
    
    snippet_lines = []
    for i in range(start_idx, end_idx + 1):
        line_num = i + 1
        # Highlight marker injection pointing directly to the flaw
        marker = "👉 " if line_num == int(target_line) else "   "
        snippet_lines.append(f"{marker}{line_num:4d} | {lines[i]}")
        
    return "\n".join(snippet_lines)

# ---------------------------------------------------------------------------
# MAIN SCRIPT EXECUTION
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(INPUT_CSV):
        logging.error(f"Input file '{INPUT_CSV}' not found. Please place it in this directory.")
        return

    logging.info("Starting Questionnaire Generation Pipeline...")
    df = pd.read_csv(INPUT_CSV)
    
    # Data normalization
    df.columns = df.columns.str.strip()
    df['Repo'] = df['Repo'].str.strip()
    df['File'] = df['File'].str.strip()
    
    cache = load_cache()
    questionnaire_dataset = []

    for index, row in df.iterrows():
        repo_name = row['Repo']
        file_path = row['File']
        line_num = row['Line']
        vuln_type = row['Type']
        vuln_desc = row['Description']
        
        logging.info(f"Processing row {index + 1}/{len(df)}: {repo_name} -> {file_path}:{line_num}")
        
        # 1. Resolve Project Context using Cache/LLM Strategy
        if repo_name in cache:
            logging.info(f"-> Cache hit for repository: '{repo_name}'")
            project_description = cache[repo_name]
        else:
            logging.info(f"-> Cache miss. Fetching context and calling LLM for: '{repo_name}'")
            repo_context = fetch_repo_context_for_llm(repo_name, GITHUB_TOKEN)
            project_description = generate_ai_project_description(repo_name, repo_context)
            
            # Persist to disk instantly to prevent loss on unexpected terminations
            cache[repo_name] = project_description
            save_cache(cache)
            time.sleep(1) # Graceful pacing boundary

        # 2. Download and slice source code target
        file_content = fetch_github_file_with_retry(repo_name, file_path, GITHUB_TOKEN)
        formatted_code_snippet = extract_code_snippet(file_content, line_num, context_lines=10)
        
        # 3. Compile everything into standard survey layout
        record = {
            # Metadata Block
            "meta_repository_name": repo_name,
            "meta_repository_url": f"https://github.com/{repo_name}",
            "meta_vulnerability_type": vuln_type,
            "meta_cwe_id": CWE_MAPPING.get(vuln_type, "N/A - Contextual Rule Flaw"),
            "meta_vulnerable_file": file_path,
            "meta_vulnerable_line": int(line_num),
            "meta_original_scanner_description": vuln_desc,
            
            # Content Block
            "content_ai_project_description": project_description,
            "content_formatted_code_snippet": formatted_code_snippet,
            
            # Explicit Google Forms / Survey Template Field Definitions
            "question_1_is_vulnerable": "Is this code actually vulnerable given the repository's context? (Options: Yes / No)",
            "question_2_severity": "How severe is this vulnerability? (Options: Low / Medium / High / Critical)",
            "question_3_confidence": "What is your confidence in this specific assessment? (Options: 1 - Lowest to 5 - Highest)",
            "question_4_description_accuracy": f"Is the scanner's rule statement accurate ('{vuln_desc}')? (Options: Yes / No)",
            "question_5_comments": "Please provide any additional comments or remediation insights regarding this instance:"
        }
        
        questionnaire_dataset.append(record)

    # Export 1: Structured JSON Data
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(questionnaire_dataset, f, indent=4, ensure_ascii=False)
    logging.info(f"Successfully generated structured file: {OUTPUT_JSON}")

    # Export 2: Flat CSV File for structural import into Qualtrics or MS Forms matrix lists
    df_output = pd.DataFrame(questionnaire_dataset)
    df_output.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_ALL)
    logging.info(f"Successfully generated matrix file: {OUTPUT_CSV}")
    
    logging.info("Pipeline Execution Completed.")

if __name__ == "__main__":
    main()
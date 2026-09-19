import os
from dotenv import load_dotenv

env_path = "C:/Users/Yashvardhan Singh/.gemini/antigravity/scratch/cognicode-engine/.env"

if not os.path.exists(env_path):
    print(f"ERROR: .env file does not exist at {env_path}")
    exit(1)

load_dotenv(env_path, override=True)

openai_key = os.getenv("OPENAI_API_KEY", "").strip()
groq_key = os.getenv("GROQ_API_KEY", "").strip()
gh_token = os.getenv("GITHUB_TOKEN", "").strip()
gh_repo = os.getenv("GITHUB_REPOSITORY", "").strip()

print("--- CogniCode .env Validation ---")
if openai_key and not openai_key.startswith("your-"):
    masked = openai_key[:6] + "..." + openai_key[-4:]
    print(f"[OK] OPENAI_API_KEY is configured ({masked})")
else:
    print("[WARNING] OPENAI_API_KEY is missing, empty, or still placeholder")

if groq_key and not groq_key.startswith("your-"):
    masked = groq_key[:6] + "..." + groq_key[-4:]
    print(f"[OK] GROQ_API_KEY is configured ({masked})")
else:
    print("[INFO] GROQ_API_KEY is not set (optional)")

if gh_token and not gh_token.startswith("your-"):
    masked = gh_token[:4] + "..." + gh_token[-3:]
    print(f"[OK] GITHUB_TOKEN is configured ({masked})")
else:
    print("[INFO] GITHUB_TOKEN is not set (optional - Local Git Mode will be used)")

if gh_repo and not gh_repo.startswith("your-"):
    print(f"[OK] GITHUB_REPOSITORY is set to '{gh_repo}'")
else:
    print("[INFO] GITHUB_REPOSITORY is not set (optional)")

# Test OpenAI connection if key present
if openai_key and not openai_key.startswith("your-"):
    print("\nTesting OpenAI API connection with gpt-4o-mini...")
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(api_key=openai_key, model="gpt-4o-mini", max_tokens=10)
        res = llm.invoke("Say 'CogniCode Ready!' in 3 words.")
        print(f"[SUCCESS] OpenAI API responded: {res.content.strip()}")
    except Exception as e:
        print(f"[ERROR] OpenAI API connection failed: {e}")

# Test Groq connection if key present
if groq_key and not groq_key.startswith("your-"):
    print("\nTesting Groq API connection...")
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(api_key=groq_key, model="openai/gpt-oss-120b", max_tokens=10)
        res = llm.invoke("Say 'Groq Ready!' in 3 words.")
        print(f"[SUCCESS] Groq API responded: {res.content.strip()}")
    except Exception as e:
        print(f"[ERROR] Groq API connection failed: {e}")

# Test GitHub connection if token present
if gh_token and not gh_token.startswith("your-"):
    print("\nTesting GitHub Token connection...")
    try:
        import requests
        resp = requests.get("https://api.github.com/user", headers={"Authorization": f"Bearer {gh_token}"}, timeout=5)
        if resp.status_code == 200:
            user_data = resp.json()
            print(f"[SUCCESS] GitHub Token authenticated for user: @{user_data.get('login')}")
        else:
            print(f"[WARNING] GitHub Token test returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[ERROR] GitHub connection failed: {e}")

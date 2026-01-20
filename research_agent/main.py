import os
import requests
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
import google.genai.errors

# 1. Smart Retry with Exponential Backoff
@retry(
    stop=stop_after_attempt(5), 
    wait=wait_exponential(multiplier=2, min=10, max=60)
)
def get_business_research():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # We define the 'google_search' tool
    search_tool = types.Tool(google_search=types.GoogleSearch())

    prompt = "Research the top 3 latest AI technology initiatives or startups in Qatar for 2026. Provide a 1-sentence summary for each."

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[search_tool]
        )
    )
    
    if response and response.text:
        return response.text
    return "No research data found today."

def send_to_discord(report):
    webhook_url = os.environ.get("DISCORD_WEBHOOK")
    if not webhook_url:
        print("❌ Error: DISCORD_WEBHOOK not found in environment.")
        return

    payload = {
        "content": f"## 📈 Qatar AI Business Update\n{report}",
        "username": "Business Scout"
    }
    
    try:
        res = requests.post(webhook_url, json=payload)
        print(f"Discord Response: {res.status_code}")
    except Exception as e:
        print(f"❌ Failed to send to Discord: {e}")

if __name__ == "__main__":
    print("🔎 Researching live web using Gemini 2.0 Flash...")
    try:
        report = get_business_research()
        print("📤 Sending to Discord...")
        send_to_discord(report)
    except Exception as e:
        print(f"❌ Automation failed after retries: {e}")
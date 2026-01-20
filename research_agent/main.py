import os
import requests
from google import genai
from google.genai import types

def get_business_research():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # We define the 'google_search' tool here
    search_tool = types.Tool(google_search=types.GoogleSearch())

    prompt = "Research the top 3 latest AI technology initiatives or startups in Qatar for 2026. Provide a 1-sentence summary for each."

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[search_tool]
        )
    )
    
    return response.text

def send_to_discord(report):
    webhook_url = os.environ.get("DISCORD_WEBHOOK")
    payload = {
        "content": f"## 📈 Qatar AI Business Update\n{report}",
        "username": "Business Scout"
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    print("🔎 Researching live web...")
    report = get_business_research()
    print("📤 Sending to Discord...")
    send_to_discord(report)
import os
import requests
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

# Keep the retry logic! It helps if the "Preview" model is busy.
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_ai_vibe(client, quote):
    prompt = f"Modern vibe check for a dev: '{quote}'"
    
    # UPDATED MODEL NAME HERE
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=prompt
    )
    return response.text

def run_task():
    # 1. Fetch Quote
    resp = requests.get("https://zenquotes.io/api/random")
    quote = resp.json()[0]['q']
    
    # 2. Setup Client
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    try:
        # 3. Get AI Insight
        vibe = get_ai_vibe(client, quote)
        
        # 4. Prepare Discord Message
        message = (
            f"**Daily Inspiration (Gemini 3 Powered):**\n"
            f"> {quote}\n\n"
            f"**🤖 AI Vibe Check:** {vibe}"
        )
        
        # 5. Send to Discord
        webhook_url = os.environ.get("DISCORD_WEBHOOK")
        if webhook_url:
            requests.post(webhook_url, json={"content": message})
            print("✅ Successfully sent Gemini 3 insight to Discord!")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    run_task()
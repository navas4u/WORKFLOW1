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
    resp = requests.get("https://zenquotes.io/api/random")
    quote = resp.json()[0]['q']
    
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    try:
        vibe = get_ai_vibe(client, quote)
        # --- NEW: SAFETY TRUNCATION ---
        # Discord limit is 2000. We leave room for the quote and formatting.
        max_length = 1800 
        if len(vibe) > max_length:
            vibe = vibe[:max_length] + "... [Truncated]"
        # ------------------------------
        # Check if vibe is empty
        if not vibe:
            vibe = "AI was speechless today!"

        payload = {
            "content": f"**Daily Inspiration:**\n> {quote}\n\n**🤖 AI Vibe Check:** {vibe}",
            "username": "Gemini 3 Bot" # This helps you see if it's working
        }
        
        webhook_url = os.environ.get("DISCORD_WEBHOOK")
        if webhook_url:
            result = requests.post(webhook_url, json=payload)
            
            # This is the "Truth" line:
            print(f"Discord Response Code: {result.status_code}")
            
            if result.status_code == 204:
                print("✅ Discord accepted the message (204). It MUST be in the channel!")
            else:
                print(f"⚠️ Discord responded with {result.status_code}: {result.text}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    run_task()
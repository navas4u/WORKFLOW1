import os
import requests
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

# 1. Smart Retry Logic for Gemini 3
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_ai_vibe(client, quote):
    # Prompt for Malayalam historical context
    prompt = f"Give some examples from history (max 3 sentences) regarding this in Malayalam: '{quote}'"
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=prompt
    )
    
    # CRITICAL: Return the text if it exists, otherwise return None
    if response and response.text:
        return response.text
    return None

def run_task():
    # 2. Check Memory (History)
    history_file = "history.txt"
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            f.write("--- Quote History ---\n")
    
    with open(history_file, "r") as f:
        past_quotes = f.read().splitlines()

    # 3. Fetch a Unique Quote
    new_quote = ""
    author = ""
    for _ in range(5): 
        resp = requests.get("https://zenquotes.io/api/random")
        data = resp.json()[0]
        if data['q'] not in past_quotes:
            new_quote = data['q']
            author = data['a']
            break
    
    if not new_quote:
        print("Could not find a unique quote after 5 tries.")
        return

    # 4. Setup Gemini Client
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    try:
        # 5. Get AI insight with Safety Check
        vibe = get_ai_vibe(client, new_quote)
        
        # If Gemini returned None or empty, use a safe fallback string
        if not vibe:
            vibe = "ഈ ഉദ്ധരണിയെക്കുറിച്ച് കൂടുതൽ വിവരങ്ങൾ ഇപ്പോൾ ലഭ്യമല്ല. (AI Safety Filter active)."

        # 6. Safety Truncation for Discord (Total length < 2000)
        # We use 1700 to leave plenty of room for the quote and formatting
        if len(vibe) > 1700:
            vibe = vibe[:1700] + "... [Truncated]"

        # 7. Save to History (Only if we successfully processed it)
        with open(history_file, "a") as f:
            f.write(new_quote + "\n")

        # 8. Send to Discord
        payload = {
            "content": f"**Daily Inspiration:**\n> {new_quote}\n— *{author}*\n\n**🤖 AI Vibe Check (Malayalam):**\n{vibe}",
            "username": "Gemini 3 Bot"
        }
        
        webhook_url = os.environ.get("DISCORD_WEBHOOK")
        if webhook_url:
            result = requests.post(webhook_url, json=payload)
            print(f"Discord Response Code: {result.status_code}")
            if result.status_code == 204:
                print("✅ Success! History updated and message sent.")
            else:
                print(f"⚠️ Discord Error: {result.text}")
                
    except Exception as e:
        print(f"❌ Automation failed: {e}")

if __name__ == "__main__":
    run_task()